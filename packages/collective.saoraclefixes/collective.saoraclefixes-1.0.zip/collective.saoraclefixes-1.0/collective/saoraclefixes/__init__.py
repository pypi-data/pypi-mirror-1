import logging
import sqlalchemy as sa

logger = logging.getLogger('collective.saoraclefixes')


def getSAVersion():
    try:
        version = sa.__version__
        return version, tuple(int(v) for v in version[:4].split('.') if v)
    except (AttributeError, ValueError):
        logger.debug("Failed to find SQLAlchemy's version, exiting")
        return None, None


def checkSAVersion():
    """Test for correct SQLAlchemy versions"""
    version, components = getSAVersion()
    if version is None:
        return False
    if components[0] > 0 or components[1] > 5:
        logger.debug('SQLAlchemy version %s is too new', version)
        return False
    if components[1] < 4:
        logger.debug('SQLAlchemy version %s is too old', version)
        return False
    logger.debug('Found SQLAlchemy version %s', version)
    return True


def checkClasses():
    """Test for expected classes"""
    from sqlalchemy.databases import oracle
    try:
        if (oracle.dialect.preparer is not oracle.OracleIdentifierPreparer or
            oracle.dialect.statement_compiler is not oracle.OracleCompiler):
            logger.debug('Unexpected Oracle dialect classes found')
            return False

        if getSAVersion()[1][1] == 4:
            create_execution_context = oracle.dialect.create_execution_context
            cec_code = create_execution_context.im_func.func_code
            if (cec_code.co_nlocals != 3 or 
                cec_code.co_names[:1] != ('OracleExecutionContext',)):
                logger.debug(
                    'Unexpected Oracle dialect execution context found')
                return False
            if oracle.dialect is not oracle.OracleDialect:
                logger.debug('Unexpected Oracle dialect classes found')
                return False
        else:
            if (oracle.dialect.execution_ctx_cls is not 
                oracle.OracleExecutionContext):
                logger.debug('Unexpected Oracle dialect classes found')
                return False
    except AttributeError:
        logger.debug('Unexpected attribute error when testing Oracle dialect '
                     'classes')
        return False
    return True


def applyPatches():
    """Wrap Oracle driver classes in sub-classes with added functionality"""
    from sqlalchemy.databases import oracle
    
    # Extended execution context to deal with quoted bind parameters;
    # ingoing parameters must match the quoted bind parameter names
    class PatchedOracleExecutionContext(oracle.OracleExecutionContext):
        def pre_exec(self):
            """Replace parameters with quoted equivalents"""
            quoted = getattr(self.compiled, '_quoted_bind_names', {})
            if quoted:
                encoding = self.dialect.encoding
                for param in self.parameters:
                    for fromname, toname in quoted.iteritems():
                        param[toname.encode(encoding)] = param[fromname]
                        del param[fromname]

            if self.dialect.auto_setinputsizes:
                self.set_input_sizes()

            if len(self.compiled_parameters) == 1:
                for key, bindparam in self.compiled.binds.iteritems():
                    if bindparam.isoutparam:
                        name = self.compiled.bind_names[bindparam]
                        value = self.compiled_parameters[0][name]
                        type_ = bindparam.type.dialect_impl(self.dialect)
                        dbtype = type_.get_dbapi_type(self.dialect.dbapi)
                        if not hasattr(self, 'out_parameters'):
                            self.out_parameters = {}
                        out_param = self.cursor.var(dbtype)
                        self.out_parameters[name] = out_param
                        self.parameters[0][quoted.get(name, name)] = out_param

        def set_input_sizes(self):
            inputsizes = {}
            quoted = getattr(self.compiled, '_quoted_bind_names', {})
            exclude = (self.dialect.dbapi.STRING,)
            for bindparam, key in self.compiled.bind_names.iteritems():
                type_ = bindparam.type.dialect_impl(self.dialect)
                dbtype = type_.get_dbapi_type(self.dialect.dbapi)
                if dbtype is not None and dbtype not in exclude:
                    key = quoted.get(key, key).encode(self.dialect.encoding)
                    inputsizes[key] = dbtype
            try:
                self.cursor.setinputsizes(**inputsizes)
            except Exception, e:
                self._connection._handle_dbapi_exception(e, None, None, None)
                raise

    if getSAVersion()[1][1] == 4:
        # SQLAlchemy 0.4 hardcoded the execution context inside a method
        class PatchedOracleDialect(oracle.OracleDialect):
            def create_execution_context(self, *args, **kwargs):
                """Use our patched execution context"""
                return PatchedOracleExecutionContext(self, *args, **kwargs)
        oracle.dialect = PatchedOracleDialect
        # SQLAlchemy still has util.Set to support older python versions
        Set = sa.util.Set
    else:
        oracle.dialect.execution_ctx_cls = PatchedOracleExecutionContext
        Set = set

    # Oracle reserved words; these are auto-quoted by SQLAlchemy
    # Also add a utility method to determine what bind parameters need quoting
    # Missing keywords taken from the query:
    #    SELECT keyword FROM v$reserved_words
    #    WHERE (reserved = 'Y' OR res_semi = 'Y') AND length > 1
    #    ORDER BY keyword;
    # See http://bit.ly/nZkeD for table documentation
    # This is a superset of the set in SQLAlchemy 0.6, which omits res_semi
    # keywords.    
    RESERVED_WORDS = Set([
        'access', 'add', 'all', 'alter', 'and', 'any', 'as', 'asc', 'audit',
        'between', 'by', 'char', 'check', 'cluster', 'column', 'comment',
        'compress', 'connect', 'create', 'current', 'date', 'decimal',
        'default', 'delete', 'desc', 'distinct', 'drop', 'else', 'exclusive',
        'exists', 'file', 'float', 'for', 'from', 'grant', 'group', 'having',
        'identified', 'immediate', 'in', 'increment', 'index', 'initial',
        'insert', 'integer', 'intersect', 'into', 'is', 'level', 'like',
        'lock', 'long', 'maxextents', 'minus', 'mlslabel', 'mode', 'modify',
        'noaudit', 'nocompress', 'not', 'nowait', 'null', 'number', 'of',
        'offline', 'on', 'online', 'option', 'or', 'order', 'pctfree',
        'prior', 'privileges', 'public', 'raw', 'rename', 'resource',
        'revoke', 'row', 'rowid', 'rownum', 'rows', 'select', 'session',
        'set', 'share', 'size', 'smallint', 'start', 'successful', 'synonym',
        'sysdate', 'table', 'then', 'to', 'trigger', 'uid', 'union', 'unique',
        'update', 'user', 'validate', 'values', 'varchar', 'varchar2', 'view',
        'whenever', 'where', 'with',
    ])

    class PatchedOracleIdentifierPreparer(oracle.OracleIdentifierPreparer):
        reserved_words = RESERVED_WORDS

        def _bindparam_requires_quotes(self, value):
            """Return True if the given identifier requires quoting."""
            lc_value = value.lower()
            return (lc_value in self.reserved_words
                    or self.illegal_initial_characters.match(value[0])
                    or not self.legal_characters.match(unicode(value))
                    )

    oracle.dialect.preparer = PatchedOracleIdentifierPreparer

    class PatchedOracleCompiler(oracle.OracleCompiler):
        def __init__(self, *args, **kwargs):
            super(PatchedOracleCompiler, self).__init__(*args, **kwargs)
            self._quoted_bind_names = {}

        def bindparam_string(self, name):
            """Quote bind parameters if so required"""
            if self.preparer._bindparam_requires_quotes(name):
                quoted_name = '"%s"' % name
                self._quoted_bind_names[name] = name = quoted_name
            return super(PatchedOracleCompiler, self).bindparam_string(name)

    oracle.dialect.statement_compiler = PatchedOracleCompiler


if checkSAVersion() and checkClasses():
    logger.debug('Applying patch')
    applyPatches()
else:
    logger.debug('Skipping patch')
