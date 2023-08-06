sgawidgets

This is a TurboGears (http://www.turbogears.org) widget project.
You can view the widgets in the Toolbox.

Estos son los pasos que se han tomado para poder construir este widget pkg

1) tg-admin quickstart -t tgwidget sgawidgets

2) Poner los recursos estáticos en el directorio static y registrarlo con la 
funcion: turbogears.widgets.register_static_directory

3) Modificar el sgawidgets/__init__.py e importar lo que queremos publicar

4) Crear subclases de WidgetDescription para que asomen en el toolbox

4.5) Llenar la info de sgawidgets/release.py con la información acorde al
plugin

5) Terminado el plugin:
   - borramos todo rastro previo del plugin en /usr/local/lib/python*/site-packages/miplugin-*
   - ejecutar python setup.py develop o python setup.py bdist_egg para crear un
     huevo
   - instalar con easy_install

6) Para subirlo al cheesse shop:
   python setup.py upload
