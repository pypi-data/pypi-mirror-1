INCLUDES = $(PYTHON_INCLUDES) $(PYGTK_CFLAGS) $(GTKIMAGEVIEW_CFLAGS)

# Twiddle with the install path. Package is named pygtkimageview but I
# want the .so-file to be installed in site-packages/gtkimageview.
pkgpyexecdir = $(pyexecdir)/gtkimageview
pkgpyexec_PYTHON = __init__.py

# GtkImageView binding
pkgpyexec_LTLIBRARIES = _gtkimageview.la
_gtkimageview_la_LDFLAGS = -module -avoid-version \
	--export-symbols-regex init_gtkimageview
_gtkimageview_la_SOURCES = gtkimageview.c gtkimageviewmodule.c enums-public.c 
_gtkimageview_la_INCLUDES = enums-public.h enums-private.h
_gtkimageview_la_LIBADD = $(GTKIMAGEVIEW_LIBS) $(PYTHON_LIBS)

CLEANFILES = gtkimageview.c enums-public.h enums-public.c
EXTRA_DIST =			\
	gtkimageview.defs	\
	gtkimageview.override	\
	enums-public.c		\
	enums-public.h

# Rule for creating all public enum objects. Note the hardcoded
# paths!
enums-public.h: 
	$(GLIB_MKENUMS) \
	--fhead "#ifndef __PUB_ENUMS_H__\n#define __PUB_ENUMS_H__\nG_BEGIN_DECLS" \
	--fprod "/* enumerations from \"@filename@\" */" \
	--vhead "GType @enum_name@_get_type (void) G_GNUC_CONST;\n#define GTK_TYPE_@ENUMSHORT@ (@enum_name@_get_type())\n" \
	--ftail "G_END_DECLS\n\n#endif" \
	`$(PKG_CONFIG) --variable=includedir gtkimageview`/gtkimageview/gtk*.h > $@

enums-public.c:
	$(GLIB_MKENUMS) \
	--fhead "#include <gtkimageview/gtkimageview.h>\n#include <gtkimageview/gtkimagetoolselector.h>\nG_BEGIN_DECLS\n" \
	--fprod "/* enumerations from \"@filename@\" */" \
	--vhead "GType\n@enum_name@_get_type (void)\n{\n  static GType etype = 0;\n  if (etype == 0) {\n    static const G@Type@Value values[] = {" \
	--vprod "      { @VALUENAME@, \"@VALUENAME@\", \"@valuenick@\" }," \
	--vtail "      { 0, NULL, NULL }\n    };\n    etype = g_@type@_register_static (g_intern_static_string (\"@EnumName@\"), values);\n  }\n  return etype;\n}\n" \
	`$(PKG_CONFIG) --variable=includedir gtkimageview`/gtkimageview/gtk*.h > $@

gtkimageview.c: gtkimageview.defs gtkimageview.override enums-public.h

.defs.c:
	$(PYGTK_CODEGEN) \
	    -r $(PYGTK_DEFSDIR)/gdk-types.defs \
	    -r $(PYGTK_DEFSDIR)/gtk-types.defs \
	    -o $*.override \
	    --prefix $* $*.defs > $*.c
