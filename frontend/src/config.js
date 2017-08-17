module.exports = {
  rethinkdb: {
    host: 'localhost',
    port: 28015,
    authKey: '',
    db: 'semantic_renewability_db',
    table_experiments: 'experiments',
    table_transformations: 'transformations',
    table_analytics: 'analytics',
    table_tests : 'tests'
  },
  express: {
     port: 3000
  }
};