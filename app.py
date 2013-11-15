from flask import Flask, jsonify, Response, request, json
from penn.registrar import Registrar
app = Flask(__name__)


@app.route('/course/<string:course_id>')
def listSectionStatus(course_id):
    r= Registrar("UPENN_OD_emmK_1000220", "2g0rbtdurlau4didkj9schee95")
    cis100s = r.search({'course_id': course_id})
    i=0
    d = {}
    for x in cis100s:
        print x["section_id"]
        s = x["section_id"]
        print s
        if x["is_closed"]:
            d[s] = "closed"
        else:
            d[s] = "open"
    return jsonify(d)





if __name__ == '__main__':
    app.run(debug=True)
