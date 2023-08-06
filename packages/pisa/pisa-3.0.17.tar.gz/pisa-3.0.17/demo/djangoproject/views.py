from django import http
from django.shortcuts import render_to_response
from ezpdf import render_to_pdf
import sx.pisa3 as pisa
import cStringIO as StringIO

def index(request):
    return http.HttpResponse("""
        <html><body>
            <h1>Example 1</h1>
            Please enter some HTML code:
            <form action="/download/" method="post" enctype="multipart/form-data">
            <textarea name="data">Hello <strong>World</strong></textarea>
            <br />
            <input type="submit" value="Convert HTML to PDF" />
            </form>
            <hr>
            <h1>Example 2</h1>
            <p><a href="ezpdf_sample">Example with template</a>
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

def ezpdf_sample(request):
    blog_entries = []
    for i in range(1,10):
        blog_entries.append({
            'id': i,
            'title':'Playing with pisa 3.0.16 and dJango Template Engine',
            'body':'This is a simple example..'
            })
    return render_to_pdf('entries.html',{
        'pagesize':'A4',
        'title':'My amazing blog',
        'blog_entries':blog_entries})
