from django import http
import sx.pisa3 as pisa
import cStringIO as StringIO

def index(request):
    return http.HttpResponse("""
        <html><body>
            Please enter some HTML code:
            <form action="/download/" method="post" enctype="multipart/form-data">
            <textarea name="data">Hello <strong>World</strong></textarea>
            <br />
            <input type="submit" value="Convert HTML to PDF" />
            </form>
        </body></html>
        """)

def download(request):
    if request.POST:
        result = StringIO.StringIO()
        pdf = pisa.CreatePDF(
            StringIO.StringIO(request.POST["data"]),
            result
            )

        if not pdf.err:
            return http.HttpResponse(
                result.getvalue(),
                mimetype='application/pdf')

    return http.HttpResponse('We had some errors')
