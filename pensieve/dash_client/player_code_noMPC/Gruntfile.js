module.exports = function(grunt) {
  grunt.initConfig({
    connect: {
      default_options: {},
      dev: {
        options: {
          port: 9999,
          keepalive: true
        }
      }
    },
    watch: {},
    jshint: {
      all: ["app/js/*/**/*.js"],
      options: {
        jshintrc: ".jshintrc"
      }
    },
    uglify : {
      min : {
        files: {
          "dash.min.js" : [
            "app/js/streaming/MediaPlayer.js",
            "app/js/streaming/Context.js",
            "app/js/dash/Dash.js",
            "app/js/dash/DashContext.js",
            "app/lib/q.js",
            "app/lib/xml2json.js",
            "app/lib/objectiron.js",
            "app/lib/dijon.js",
            "app/js/*/**/*.js"],
        }
      },
      all : {
        files: {
          "dash.all.js" : [
            "./app/lib/q.js",
            "./app/lib/xml2json.js",
            "./app/lib/objectiron.js",
            "./app/lib/dijon.js",
            "./app/lib/Math.js",
            "./app/lib/long.js",
            "./app/lib/base64.js",
	    "./app/lib/jquery/jquery-1.10.2.min.js",
            "./app/js/streaming/MediaPlayer.js",
            "./app/js/streaming/Context.js",
            "./app/js/dash/Dash.js",
            "./app/js/dash/DashContext.js",
            "./app/js/*/**/*.js"]
        }
      }
    },
    jasmine: {
      tests: {
        src: [
            "./app/js/streaming/MediaPlayer.js",
            "./app/js/streaming/Context.js",
            "./app/js/dash/Dash.js",
            "./app/js/dash/DashContext.js",
            "./app/js/*/**/*.js"],

        options: {
          host: 'http://127.0.0.1:8000/',
          keepRunner: true,
          helpers: [
            "./test/js/utils/MPDfiles.js",
            "./test/js/utils/Utils.js",
            "./test/js/utils/ValidateUrl.js",
            "./app/js/Main.js"],
          specs: [
            './test/js/dash/DashParser_Suite.js',
             './test/js/dash/FragmentExtensions_Suite.js',
             './test/js/dash/DashMetricsExtensions_Suite.js',
             './test/js/dash/DashMetricsConverter_Suite.js',
             './test/js/dash/DashManifestExtensions_Suite.js',
             './test/js/dash/DashManifestExtensionsNeg_Suite.js',
             './test/js/dash/DashHandler_Suite.js',
             './test/js/streaming/MediaPlayer_Suite.js',
             './test/js/streaming/Stream_Suite.js',
             './test/js/streaming/AbrController_Suite.js',
             './test/js/streaming/BufferController_Suite.js',
             './test/js/streaming/Capabilities_Suite.js',
             './test/js/streaming/MetricsModel_Suite.js',
             './test/js/streaming/ManifestUpdater_Suite.js',
             './test/js/streaming/FragmentController_Suite.js',
             "./test/js/streaming/VideoModel_Suite.js",
             './test/js/streaming/ManifestLoader_Suite.js'
			],
          vendor: [
			"./app/lib/jquery/jquery-1.10.2.min.js",
            "./app/lib/q.js",
            "./app/lib/xml2json.js",
            "./app/lib/objectiron.js",			
            "./app/lib/Math.js",
            "./app/lib/long.js",
            "./app/lib/kendo/kendo.web.min.js", 
			"./app/lib/dijon.js",
            "./app/lib/base64.js"],
          template : require('grunt-template-jasmine-istanbul'),
          templateOptions: {
            coverage: 'reports/coverage.json',
            report: 'reports/coverage'},
          junit: {
              path: grunt.option('jsunit-path'),
              consolidate: true}
        }
      }
    }
  });

  // Require needed grunt-modules
  //grunt.loadNpmTasks('grunt-contrib-connect');
  //grunt.loadNpmTasks('grunt-contrib-watch');
  //grunt.loadNpmTasks('grunt-contrib-jasmine');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');


  // Define tasks
  //grunt.registerTask('default', ['jshint','connect:default_options','jasmine','uglify']);
	// Xiaoqi_new
	grunt.registerTask('default', ['jshint','uglify']);
	// Xiaoqi_new
};
