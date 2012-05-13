import os
import tempfile
import subprocess

# TODO: make asynchronous
def convert(f):
  tmp_in_fn = tempfile.mktemp()
  tmp_in_fd = open(tmp_in_fn, 'wc')
  tmp_in_fd.write(f.data)
  tmp_in_fd.close()

  tmp_out_fn = tempfile.mktemp()

  if f.mime_type == 'application/pdf':
    print subprocess.__file__
    print 'pdftotext', tmp_in_fn, tmp_out_fn
    subprocess.check_output(['/usr/local/bin/pdftotext', tmp_in_fn, tmp_out_fn])
    text = open(tmp_out_fn).read()
    f.text = unicode(text, 'utf8', errors='ignore')
    os.unlink(tmp_out_fn)

    subprocess.check_output(['pdftoppm', '-singlefile', '-jpeg', '-l', '1', tmp_in_fn, tmp_out_fn])
    preview = open(tmp_out_fn + '.jpg').read()
    f.preview = preview
    print tmp_out_fn + '.jpg'
    #os.unlink(tmp_out_fn)

  os.unlink(tmp_in_fn)
