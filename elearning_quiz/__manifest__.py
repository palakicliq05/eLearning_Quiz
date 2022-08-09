{
    'name':'Elearning_quiz',
    'version' : '1.1',
    'author': 'weblearns',
    'summary' :'elearning quiz ',
    'sequence' : 1,
    'description' : "elearning quiz"
                    "odoo v15",
    'category' : 'Inventory Audit',                
    'website' : 'https://freeweblearns.blogspot.com',
    'depends': ['base',"survey"],
    'data' : [
        "views/survey_inherit_modify.xml",
        "views/template_inherit.xml",
        "views/survey_template_statistics_inherit.xml",
        "views/survey_form_inherit_js.xml"

    ],
    
    'assets':{
        'survey.survey_assets':[
            'elearning_quiz/static/src/js/survey_form_inherit.js'
        ]
    }
    

}