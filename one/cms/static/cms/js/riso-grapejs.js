var lp = './img/';
var plp = 'https://via.placeholder.com/350x250/';
var images = [
    lp + 'team1.jpg',
    lp + 'team2.jpg',
    lp + 'team3.jpg',
    plp + '78c5d6/fff',
    plp + '459ba8/fff',
    plp + '79c267/fff',
    plp + 'c5d647/fff',
    plp + 'f28c33/fff',
    plp + 'e868a2/fff',
    plp + 'cc4360/fff',
    lp + 'work-desk.jpg',
    lp + 'phone-app.png',
    lp + 'bg-gr-v.png'
];

var editor;
// grapesjs.init({
//     height: '500px',
//     container : '#gjs',
//     fromElement: true,
//     showOffsets: true,
//     assetManager: {
//       embedAsBase64: true,
//       assets: images
//     },
//     selectorManager: { componentFirst: true },
//     styleManager: {
//       sectors: [{
//           name: 'General',
//           properties:[
//             {
//               extend: 'float',
//               type: 'radio',
//               default: 'none',
//               options: [
//                 { value: 'none', className: 'fa fa-times'},
//                 { value: 'left', className: 'fa fa-align-left'},
//                 { value: 'right', className: 'fa fa-align-right'}
//               ],
//             },
//             'display',
//             { extend: 'position', type: 'select' },
//             'top',
//             'right',
//             'left',
//             'bottom',
//           ],
//         }, {
//             name: 'Dimension',
//             open: false,
//             properties: [
//               'width',
//               {
//                 id: 'flex-width',
//                 type: 'integer',
//                 name: 'Width',
//                 units: ['px', '%'],
//                 property: 'flex-basis',
//                 toRequire: 1,
//               },
//               'height',
//               'max-width',
//               'min-height',
//               'margin',
//               'padding'
//             ],
//           },{
//             name: 'Typography',
//             open: false,
//             properties: [
//                 'font-family',
//                 'font-size',
//                 'font-weight',
//                 'letter-spacing',
//                 'color',
//                 'line-height',
//                 {
//                   extend: 'text-align',
//                   options: [
//                     { id : 'left',  label : 'Left',    className: 'fa fa-align-left'},
//                     { id : 'center',  label : 'Center',  className: 'fa fa-align-center' },
//                     { id : 'right',   label : 'Right',   className: 'fa fa-align-right'},
//                     { id : 'justify', label : 'Justify',   className: 'fa fa-align-justify'}
//                   ],
//                 },
//                 {
//                   property: 'text-decoration',
//                   type: 'radio',
//                   default: 'none',
//                   options: [
//                     { id: 'none', label: 'None', className: 'fa fa-times'},
//                     { id: 'underline', label: 'underline', className: 'fa fa-underline' },
//                     { id: 'line-through', label: 'Line-through', className: 'fa fa-strikethrough'}
//                   ],
//                 },
//                 'text-shadow'
//             ],
//           },{
//             name: 'Decorations',
//             open: false,
//             properties: [
//               'opacity',
//               'border-radius',
//               'border',
//               'box-shadow',
//               'background', // { id: 'background-bg', property: 'background', type: 'bg' }
//             ],
//           },{
//             name: 'Extra',
//             open: false,
//             buildProps: [
//               'transition',
//               'perspective',
//               'transform'
//             ],
//           },{
//             name: 'Flex',
//             open: false,
//             properties: [{
//               name: 'Flex Container',
//               property: 'display',
//               type: 'select',
//               defaults: 'block',
//               list: [
//                 { value: 'block', name: 'Disable'},
//                 { value: 'flex', name: 'Enable'}
//               ],
//             },{
//               name: 'Flex Parent',
//               property: 'label-parent-flex',
//               type: 'integer',
//             },{
//               name: 'Direction',
//               property: 'flex-direction',
//               type: 'radio',
//               defaults: 'row',
//               list: [{
//                 value: 'row',
//                 name: 'Row',
//                 className: 'icons-flex icon-dir-row',
//                 title: 'Row',
//               },{
//                 value: 'row-reverse',
//                 name: 'Row reverse',
//                 className: 'icons-flex icon-dir-row-rev',
//                 title: 'Row reverse',
//               },{
//                 value: 'column',
//                 name: 'Column',
//                 title: 'Column',
//                 className: 'icons-flex icon-dir-col',
//               },{
//                 value: 'column-reverse',
//                 name: 'Column reverse',
//                 title: 'Column reverse',
//                 className: 'icons-flex icon-dir-col-rev',
//               }],
//             },{
//               name: 'Justify',
//               property: 'justify-content',
//               type: 'radio',
//               defaults: 'flex-start',
//               list: [{
//                 value: 'flex-start',
//                 className: 'icons-flex icon-just-start',
//                 title: 'Start',
//               },{
//                 value: 'flex-end',
//                 title: 'End',
//                 className: 'icons-flex icon-just-end',
//               },{
//                 value: 'space-between',
//                 title: 'Space between',
//                 className: 'icons-flex icon-just-sp-bet',
//               },{
//                 value: 'space-around',
//                 title: 'Space around',
//                 className: 'icons-flex icon-just-sp-ar',
//               },{
//                 value: 'center',
//                 title: 'Center',
//                 className: 'icons-flex icon-just-sp-cent',
//               }],
//             },{
//               name: 'Align',
//               property: 'align-items',
//               type: 'radio',
//               defaults: 'center',
//               list: [{
//                 value: 'flex-start',
//                 title: 'Start',
//                 className: 'icons-flex icon-al-start',
//               },{
//                 value: 'flex-end',
//                 title: 'End',
//                 className: 'icons-flex icon-al-end',
//               },{
//                 value: 'stretch',
//                 title: 'Stretch',
//                 className: 'icons-flex icon-al-str',
//               },{
//                 value: 'center',
//                 title: 'Center',
//                 className: 'icons-flex icon-al-center',
//               }],
//             },{
//               name: 'Flex Children',
//               property: 'label-parent-flex',
//               type: 'integer',
//             },{
//               name: 'Order',
//               property: 'order',
//               type: 'integer',
//               defaults: 0,
//               min: 0
//             },{
//               name: 'Flex',
//               property: 'flex',
//               type: 'composite',
//               properties  : [{
//                 name: 'Grow',
//                 property: 'flex-grow',
//                 type: 'integer',
//                 defaults: 0,
//                 min: 0
//               },{
//                 name: 'Shrink',
//                 property: 'flex-shrink',
//                 type: 'integer',
//                 defaults: 0,
//                 min: 0
//               },{
//                 name: 'Basis',
//                 property: 'flex-basis',
//                 type: 'integer',
//                 units: ['px','%',''],
//                 unit: '',
//                 defaults: 'auto',
//               }],
//             },{
//               name: 'Align',
//               property: 'align-self',
//               type: 'radio',
//               defaults: 'auto',
//               list: [{
//                 value: 'auto',
//                 name: 'Auto',
//               },{
//                 value: 'flex-start',
//                 title: 'Start',
//                 className: 'icons-flex icon-al-start',
//               },{
//                 value   : 'flex-end',
//                 title: 'End',
//                 className: 'icons-flex icon-al-end',
//               },{
//                 value   : 'stretch',
//                 title: 'Stretch',
//                 className: 'icons-flex icon-al-str',
//               },{
//                 value   : 'center',
//                 title: 'Center',
//                 className: 'icons-flex icon-al-center',
//               }],
//             }]
//           }
//         ],
//     },
//     plugins: [
//       'gjs-blocks-basic',
//       'grapesjs-plugin-forms',
//       'grapesjs-component-countdown',
//       'grapesjs-plugin-export',
//       'grapesjs-tabs',
//       'grapesjs-custom-code',
//       'grapesjs-touch',
//       'grapesjs-parser-postcss',
//       'grapesjs-tooltip',
//       'grapesjs-tui-image-editor',
//       'grapesjs-typed',
//       'grapesjs-style-bg',
//       'grapesjs-preset-webpage',
//     ],
//     pluginsOpts: {
//       'gjs-blocks-basic': { flexGrid: true },
//       'grapesjs-tui-image-editor': {
//         script: [
//           // 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/1.6.7/fabric.min.js',
//           'https://uicdn.toast.com/tui.code-snippet/v1.5.2/tui-code-snippet.min.js',
//           'https://uicdn.toast.com/tui-color-picker/v2.2.7/tui-color-picker.min.js',
//           'https://uicdn.toast.com/tui-image-editor/v3.15.2/tui-image-editor.min.js'
//         ],
//         style: [
//           'https://uicdn.toast.com/tui-color-picker/v2.2.7/tui-color-picker.min.css',
//           'https://uicdn.toast.com/tui-image-editor/v3.15.2/tui-image-editor.min.css',
//         ],
//       },
//       'grapesjs-tabs': {
//         tabsBlock: { category: 'Extra' }
//       },
//       'grapesjs-typed': {
//         block: {
//           category: 'Extra',
//           content: {
//             type: 'typed',
//             'type-speed': 40,
//             strings: [
//               'Text row one',
//               'Text row two',
//               'Text row three',
//             ],
//           }
//         }
//       },
//       'grapesjs-preset-webpage': {
//         modalImportTitle: 'Import Template',
//         modalImportLabel: '<div style="margin-bottom: 10px; font-size: 13px;">Paste here your HTML/CSS and click Import</div>',
//         modalImportContent: function(editor) {
//           return editor.getHtml() + '<style>'+editor.getCss()+'</style>'
//         },
//       },
//     },
//   });

function initGrapesjs() {
    return grapesjs.init({
        height: '1000px',
        container: '#gjs',
        fromElement: true,
        showOffsets: true,
        assetManager: {
            embedAsBase64: true,
            assets: images
        },
        selectorManager: {componentFirst: true},
        styleManager: {
            sectors: [{
                name: 'General',
                properties: [
                    {
                        extend: 'float',
                        type: 'radio',
                        default: 'none',
                        options: [
                            {value: 'none', className: 'fa fa-times'},
                            {value: 'left', className: 'fa fa-align-left'},
                            {value: 'right', className: 'fa fa-align-right'}
                        ],
                    },
                    'display',
                    {extend: 'position', type: 'select'},
                    'top',
                    'right',
                    'left',
                    'bottom',
                ],
            }, {
                name: 'Dimension',
                open: false,
                properties: [
                    'width',
                    {
                        id: 'flex-width',
                        type: 'integer',
                        name: 'Width',
                        units: ['px', '%'],
                        property: 'flex-basis',
                        toRequire: 1,
                    },
                    'height',
                    'max-width',
                    'min-height',
                    'margin',
                    'padding'
                ],
            }, {
                name: 'Typography',
                open: false,
                properties: [
                    'font-family',
                    'font-size',
                    'font-weight',
                    'letter-spacing',
                    'color',
                    'line-height',
                    {
                        extend: 'text-align',
                        options: [
                            {id: 'left', label: 'Left', className: 'fa fa-align-left'},
                            {id: 'center', label: 'Center', className: 'fa fa-align-center'},
                            {id: 'right', label: 'Right', className: 'fa fa-align-right'},
                            {id: 'justify', label: 'Justify', className: 'fa fa-align-justify'}
                        ],
                    },
                    {
                        property: 'text-decoration',
                        type: 'radio',
                        default: 'none',
                        options: [
                            {id: 'none', label: 'None', className: 'fa fa-times'},
                            {id: 'underline', label: 'underline', className: 'fa fa-underline'},
                            {id: 'line-through', label: 'Line-through', className: 'fa fa-strikethrough'}
                        ],
                    },
                    'text-shadow'
                ],
            }, {
                name: 'Decorations',
                open: false,
                properties: [
                    'opacity',
                    'border-radius',
                    'border',
                    'box-shadow',
                    'background', // { id: 'background-bg', property: 'background', type: 'bg' }
                ],
            }, {
                name: 'Extra',
                open: false,
                buildProps: [
                    'transition',
                    'perspective',
                    'transform'
                ],
            }, {
                name: 'Flex',
                open: false,
                properties: [{
                    name: 'Flex Container',
                    property: 'display',
                    type: 'select',
                    defaults: 'block',
                    list: [
                        {value: 'block', name: 'Disable'},
                        {value: 'flex', name: 'Enable'}
                    ],
                }, {
                    name: 'Flex Parent',
                    property: 'label-parent-flex',
                    type: 'integer',
                }, {
                    name: 'Direction',
                    property: 'flex-direction',
                    type: 'radio',
                    defaults: 'row',
                    list: [{
                        value: 'row',
                        name: 'Row',
                        className: 'icons-flex icon-dir-row',
                        title: 'Row',
                    }, {
                        value: 'row-reverse',
                        name: 'Row reverse',
                        className: 'icons-flex icon-dir-row-rev',
                        title: 'Row reverse',
                    }, {
                        value: 'column',
                        name: 'Column',
                        title: 'Column',
                        className: 'icons-flex icon-dir-col',
                    }, {
                        value: 'column-reverse',
                        name: 'Column reverse',
                        title: 'Column reverse',
                        className: 'icons-flex icon-dir-col-rev',
                    }],
                }, {
                    name: 'Justify',
                    property: 'justify-content',
                    type: 'radio',
                    defaults: 'flex-start',
                    list: [{
                        value: 'flex-start',
                        className: 'icons-flex icon-just-start',
                        title: 'Start',
                    }, {
                        value: 'flex-end',
                        title: 'End',
                        className: 'icons-flex icon-just-end',
                    }, {
                        value: 'space-between',
                        title: 'Space between',
                        className: 'icons-flex icon-just-sp-bet',
                    }, {
                        value: 'space-around',
                        title: 'Space around',
                        className: 'icons-flex icon-just-sp-ar',
                    }, {
                        value: 'center',
                        title: 'Center',
                        className: 'icons-flex icon-just-sp-cent',
                    }],
                }, {
                    name: 'Align',
                    property: 'align-items',
                    type: 'radio',
                    defaults: 'center',
                    list: [{
                        value: 'flex-start',
                        title: 'Start',
                        className: 'icons-flex icon-al-start',
                    }, {
                        value: 'flex-end',
                        title: 'End',
                        className: 'icons-flex icon-al-end',
                    }, {
                        value: 'stretch',
                        title: 'Stretch',
                        className: 'icons-flex icon-al-str',
                    }, {
                        value: 'center',
                        title: 'Center',
                        className: 'icons-flex icon-al-center',
                    }],
                }, {
                    name: 'Flex Children',
                    property: 'label-parent-flex',
                    type: 'integer',
                }, {
                    name: 'Order',
                    property: 'order',
                    type: 'integer',
                    defaults: 0,
                    min: 0
                }, {
                    name: 'Flex',
                    property: 'flex',
                    type: 'composite',
                    properties: [{
                        name: 'Grow',
                        property: 'flex-grow',
                        type: 'integer',
                        defaults: 0,
                        min: 0
                    }, {
                        name: 'Shrink',
                        property: 'flex-shrink',
                        type: 'integer',
                        defaults: 0,
                        min: 0
                    }, {
                        name: 'Basis',
                        property: 'flex-basis',
                        type: 'integer',
                        units: ['px', '%', ''],
                        unit: '',
                        defaults: 'auto',
                    }],
                }, {
                    name: 'Align',
                    property: 'align-self',
                    type: 'radio',
                    defaults: 'auto',
                    list: [{
                        value: 'auto',
                        name: 'Auto',
                    }, {
                        value: 'flex-start',
                        title: 'Start',
                        className: 'icons-flex icon-al-start',
                    }, {
                        value: 'flex-end',
                        title: 'End',
                        className: 'icons-flex icon-al-end',
                    }, {
                        value: 'stretch',
                        title: 'Stretch',
                        className: 'icons-flex icon-al-str',
                    }, {
                        value: 'center',
                        title: 'Center',
                        className: 'icons-flex icon-al-center',
                    }],
                }]
            }
            ],
        },
        plugins: [
            'gjs-blocks-basic',
            'grapesjs-plugin-forms',
            'grapesjs-component-countdown',
            'grapesjs-plugin-export',
            'grapesjs-tabs',
            'grapesjs-custom-code',
            'grapesjs-touch',
            'grapesjs-parser-postcss',
            'grapesjs-tooltip',
            'grapesjs-tui-image-editor',
            'grapesjs-typed',
            'grapesjs-style-bg',
            'grapesjs-preset-webpage',
        ],
        pluginsOpts: {
            'gjs-blocks-basic': {flexGrid: true},
            'grapesjs-tui-image-editor': {
                script: [
                    // 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/1.6.7/fabric.min.js',
                    'https://uicdn.toast.com/tui.code-snippet/v1.5.2/tui-code-snippet.min.js',
                    'https://uicdn.toast.com/tui-color-picker/v2.2.7/tui-color-picker.min.js',
                    'https://uicdn.toast.com/tui-image-editor/v3.15.2/tui-image-editor.min.js'
                ],
                style: [
                    'https://uicdn.toast.com/tui-color-picker/v2.2.7/tui-color-picker.min.css',
                    'https://uicdn.toast.com/tui-image-editor/v3.15.2/tui-image-editor.min.css',
                ],
            },
            'grapesjs-tabs': {
                tabsBlock: {category: 'Extra'}
            },
            'grapesjs-typed': {
                block: {
                    category: 'Extra',
                    content: {
                        type: 'typed',
                        'type-speed': 40,
                        strings: [
                            'Text row one',
                            'Text row two',
                            'Text row three',
                        ],
                    }
                }
            },
            'grapesjs-preset-webpage': {
                modalImportTitle: 'Import Template',
                modalImportLabel: '<div style="margin-bottom: 10px; font-size: 13px;">Paste here your HTML/CSS and click Import</div>',
                modalImportContent: function (editor) {
                    return editor.getHtml() + '<style>' + editor.getCss() + '</style>'
                },
            },
        },
    });
}

$(function () {
    $('#btn_edit_grapejs').on('click', function () {
        if (!editor) {
            editor = initGrapesjs();
        } else {
            editor.destroy();
            editor = null;
        }

        $('#modal_quick_widget').modal('hide')
    });

    $('#btn_widget_toggle').on('click', function () {
        $.ajax({
            type: "GET", // or "GET" depending on your API
            url: "/api/themes/", // Replace with your API URL
            data: null,
            headers: {
                "X-CSRFToken": csrf_token // Include the CSRF token in the request headers
            },
            success: function (response) {
                // Handle the API response
                console.log(response);
                if (Array.isArray(response)) {
                    $('#theme_list').empty()

                    var html = '';
                    response.forEach(function (item) {
                        html += `<h4>Theme ${item.name}</h4>`

                        const templates = item.templates
                        if (Array.isArray(templates)) {
                            html += `<div class="row">`
                            templates.forEach(function (template) {
                                html += `<div class="col-6">
                                                <img src="${template.thumbnail}" alt="${template.name}" class="img-fluid">
                                                <h3>${template.name}</h3>
                                                <p>${template.description}</p>
                                            </div>
                                        `
                            })
                        }
                    });

                    $('#theme_list').html(html);
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle any errors
                console.error(xhr.responseText);
            }
        });
    })
});
