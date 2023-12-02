////////////////////////////////
// Setup
////////////////////////////////

// Gulp and package
const {src, dest, parallel, series, watch} = require('gulp');
const pjson = require('./package.json');

// Plugins
const autoprefixer = require('autoprefixer');
const browserSync = require('browser-sync').create();
const concat = require('gulp-concat');
const tildeImporter = require('node-sass-tilde-importer');
const cssnano = require('cssnano');
const imagemin = require('gulp-imagemin');
const pixrem = require('pixrem');
const plumber = require('gulp-plumber');
const postcss = require('gulp-postcss');
const reload = browserSync.reload;
const rename = require('gulp-rename');
const sass = require('gulp-sass')(require('sass'));
const spawn = require('child_process').spawn;
const uglify = require('gulp-uglify-es').default;

// Relative paths function
function pathsConfig(appName) {
    this.app = `./${pjson.name}`;
    const vendorsRoot = 'node_modules';

    return {
        vendorsJs: [
            `${vendorsRoot}/jquery/dist/jquery.js`,  // Must be first Item
            `${vendorsRoot}/@popperjs/core/dist/umd/popper.js`,
            `${vendorsRoot}/bootstrap/dist/js/bootstrap.min.js`,
            `${vendorsRoot}/moment/min/moment-with-locales.min.js`,
            `${vendorsRoot}/wnumb/wNumb.js`,
            `${vendorsRoot}/jquery-ui/dist/jquery-ui.js`,
            `${vendorsRoot}/jquery-migrate/dist/jquery-migrate.js`,
            `${vendorsRoot}/axios/dist/axios.min.js`,
            `${vendorsRoot}/lozad/dist/lozad.min.js`,
            `${vendorsRoot}/select2/dist/js/select2.full.js`,
            `${this.app}/static/js/vendors/plugins/select2.init.js`,
            `${vendorsRoot}/@eonasdan/tempus-dominus/dist/js/tempus-dominus.min.js`,
            `${this.app}/static/js/vendors/plugins/tempus-dominus.init.js`,
            `${vendorsRoot}/@eonasdan/tempus-dominus/dist/locales/de.js`,
            `${vendorsRoot}/@eonasdan/tempus-dominus/dist/plugins/customDateFormat.js`,
            `${vendorsRoot}/flatpickr/dist/flatpickr.js`,
            `${vendorsRoot}/flatpickr/dist/l10n/ar.js`,
            `${vendorsRoot}/es6-shim/es6-shim.js`,
            `${this.app}/static/plugins/@form-validation/umd/bundle/popular.min.js`,
            `${this.app}/static/plugins/@form-validation/umd/bundle/full.min.js`,
            `${this.app}/static/plugins/@form-validation/umd/plugin-bootstrap5/index.min.js`,
            `${vendorsRoot}/bootstrap-maxlength/src/bootstrap-maxlength.js`,
            `${vendorsRoot}/bootstrap-daterangepicker/daterangepicker.js`,
            `${vendorsRoot}/inputmask/dist/inputmask.js`,
            `${vendorsRoot}/inputmask/dist/bindings/inputmask.binding.js`,
            `${vendorsRoot}/tiny-slider/dist/min/tiny-slider.js`,
            `${vendorsRoot}/nouislider/dist/nouislider.js`,
            `${vendorsRoot}/autosize/dist/autosize.js`,
            `${vendorsRoot}/clipboard/dist/clipboard.min.js`,
            `${vendorsRoot}/bootstrap-multiselectsplitter/bootstrap-multiselectsplitter.js`,
            `${vendorsRoot}/smooth-scroll/dist/smooth-scroll.js`,
            `${vendorsRoot}/dropzone/dist/dropzone.js`,
            `${this.app}/static/js/vendors/plugins/dropzone.init.js`,
            `${vendorsRoot}/quill/dist/quill.js`,
            `${vendorsRoot}/@yaireo/tagify/dist/tagify.polyfills.min.js`,
            `${vendorsRoot}/@yaireo/tagify/dist/tagify.min.js`,
            `${this.app}/static/plugins/toastr/build/toastr.min.js`,
            `${vendorsRoot}/apexcharts/dist/apexcharts.min.js`,
            `${vendorsRoot}/chart.js/dist/chart.js`,
            `${vendorsRoot}/countup.js/dist/countUp.umd.js`,
            `${vendorsRoot}/es6-promise-polyfill/promise.min.js`,
            `${vendorsRoot}/sweetalert2/dist/sweetalert2.min.js`,
            `${this.app}/static/js/vendors/plugins/sweetalert2.init.js`,
        ],
        vendorsCss: [
            `${vendorsRoot}/jquery-ui/dist/themes/base/jquery-ui.css`,
            `${vendorsRoot}/select2/dist/css/select2.css`,
            `${vendorsRoot}/@eonasdan/tempus-dominus/dist/css/tempus-dominus.min.css`,
            `${vendorsRoot}/flatpickr/dist/flatpickr.css`,
            `${this.app}/static/plugins/@form-validation/umd/styles/index.css`,
            `${vendorsRoot}/bootstrap-daterangepicker/daterangepicker.css`,
            `${vendorsRoot}/tiny-slider/dist/tiny-slider.css`,
            `${vendorsRoot}/nouislider/dist/nouislider.css`,
            `${vendorsRoot}/dropzone/dist/dropzone.css`,
            `${vendorsRoot}/quill/dist/quill.snow.css`,
            `${vendorsRoot}/@yaireo/tagify/dist/tagify.css`,
            `${this.app}/static/plugins/toastr/build/toastr.css`,
            `${vendorsRoot}/apexcharts/dist/apexcharts.css`,
            `${vendorsRoot}/sweetalert2/dist/sweetalert2.css`,
            `${vendorsRoot}/line-awesome/dist/line-awesome/css/line-awesome.css`,
            `${vendorsRoot}/bootstrap-icons/font/bootstrap-icons.css`,
            `${vendorsRoot}/@fortawesome/fontawesome-free/css/all.min.css`,
        ],
        app: this.app,
        templates: `${this.app}/templates`,
        css: `${this.app}/static/css`,
        sass: `${this.app}/static/sass`,
        fonts: `${this.app}/static/fonts`,
        images: `${this.app}/static/images`,
        js: `${this.app}/static/js`,
    };
}

const paths = pathsConfig();

////////////////////////////////
// Tasks
////////////////////////////////

// Project Styles auto prefixing and minification
function styles() {
  const processCss = [
    autoprefixer(), // adds vendor prefixes
    pixrem(), // add fallbacks for rem units
  ];

  const minifyCss = [
    cssnano({ preset: 'default' }), // minify result
  ];

  return src(`${paths.sass}/project.scss`)
    .pipe(
      sass({
        importer: tildeImporter,
        includePaths: [paths.sass],
      }).on('error', sass.logError),
    )
    .pipe(plumber()) // Checks for errors
    .pipe(postcss(processCss))
    .pipe(dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(postcss(minifyCss)) // Minifies the result
    .pipe(dest(paths.css));
}

// Keenthemes Styles auto prefixing and minification
function themeStyles() {
  const processCss = [
    autoprefixer(), // adds vendor prefixes
    pixrem(), // add fallbacks for rem units
  ];

  const minifyCss = [
    cssnano({ preset: 'default' }), // minify result
  ];

  return src(`${paths.css}/theme.bundle.css`)
    .pipe(plumber()) // Checks for errors
    .pipe(postcss(processCss))
    .pipe(dest(paths.css))
    .pipe(rename({ suffix: '.min' }))
    .pipe(postcss(minifyCss)) // Minifies the result
    .pipe(dest(paths.css));
}


// Vendor Styles auto prefixing and minification
function vendorStyles() {
    const processCss = [
        autoprefixer(), // adds vendor prefixes
        pixrem(), // add fallbacks for rem units
    ];

    const minifyCss = [
        cssnano({preset: 'default'}), // minify result
    ];

    return src(paths.vendorsCss, {sourcemaps: true})
        .pipe(plumber()) // Checks for errors
        .pipe(postcss(processCss))
        .pipe(concat('vendors.bundle.css'))
        .pipe(dest(paths.css))
        .pipe(rename({suffix: '.min'}))
        .pipe(postcss(minifyCss)) // Minifies the result
        .pipe(dest(paths.css));
}


// Javascript minification
function scripts() {
    return src(`${paths.js}/project.js`)
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(rename({suffix: '.min'}))
        .pipe(dest(paths.js));
}

// Keenthemes Javascript minification
function themeScripts() {
    return src(`${paths.js}/theme.bundle.js`)
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(rename({suffix: '.min'}))
        .pipe(dest(paths.js));
}

// Vendor Javascript minification
function vendorScripts() {
    return src(paths.vendorsJs, {sourcemaps: true})
        .pipe(concat('vendors.bundle.js'))
        .pipe(dest(paths.js))
        .pipe(plumber()) // Checks for errors
        .pipe(uglify()) // Minifies the js
        .pipe(rename({suffix: '.min'}))
        .pipe(dest(paths.js, {sourcemaps: '.'}));
}

// Image compression
function imgCompression() {
    return src(`${paths.images}/*`)
        .pipe(imagemin()) // Compresses PNG, JPEG, GIF and SVG images
        .pipe(dest(paths.images));
}

// Run django server
function runServer(cb) {
    const cmd = spawn('python', ['manage.py', 'runserver'], {stdio: 'inherit'});
    cmd.on('close', function (code) {
        console.log('runServer exited with code ' + code);
        cb(code);
    });
}

// Browser sync server for live reload
function initBrowserSync() {
    browserSync.init(
        [`${paths.css}/*.css`, `${paths.js}/*.js`, `${paths.templates}/*.html`],
        {
            // https://www.browsersync.io/docs/options/#option-open
            // Disable as it doesn't work from inside a container
            open: false,
            // https://www.browsersync.io/docs/options/#option-proxy
            proxy: {
                target: 'django:8000',
                proxyReq: [
                    function (proxyReq, req) {
                        // Assign proxy 'host' header same as current request at Browsersync server
                        proxyReq.setHeader('Host', req.headers.host);
                    },
                ],
            },
        },
    );
}

// Watch
function watchPaths() {
    watch(`${paths.sass}/*.scss`, styles);
    watch(`${paths.templates}/**/*.html`).on('change', reload);
    watch([`${paths.js}/*.js`, `!${paths.js}/*.min.js`], scripts).on(
        'change',
        reload,
    );
}

// Generate all assets
const generateAssets = parallel(styles, vendorStyles, scripts, vendorScripts, imgCompression, themeStyles, themeScripts);

// Set up dev environment
const dev = parallel(initBrowserSync, watchPaths);

exports.default = series(generateAssets, dev);
exports['generate-assets'] = generateAssets;
exports['dev'] = dev;
