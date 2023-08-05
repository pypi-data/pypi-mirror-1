EPYOPTS="--no-private -v --debug --config epydoc.config"

rm -rf html pdf
PYTHONPATH=. epydoc ${EPYOPTS} --html gtkimageview

# If you don't want to generate a PDF, comment out this line
PYTHONPATH=. epydoc ${EPYOPTS} --pdf gtkimageview
