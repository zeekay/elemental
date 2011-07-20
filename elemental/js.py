from macro import js

class jquery(js):
    tag = 'jquery'
    format = '<script src="http://ajax.googleapis.com/ajax/libs/jquery/{text}/jquery.min.js"></script>'

class modernizr(js):
    tag = 'modernizr'
    format = '<script src="http://cdnjs.cloudflare.com/ajax/libs/modernizr/{text}/modernizr.min.js"></script>'
