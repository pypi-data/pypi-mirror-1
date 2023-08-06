from setuptools import setup
setup(
 name = 'accessible_output',
 author = 'Christopher Toth',
 author_email = 'q@qwitter-client.net',
 version = '0.3',
 url = 'http://www.qwitter-client.net',
 description = 'Library to provide speech and braille output to a variety of different screen readers and other accessibility solutions.',
 package_dir = {'accessible_output':''},
 packages = ['accessible_output', 'accessible_output.braille', 'accessible_output.speech', 'accessible_output.braille.outputs', 'accessible_output.speech.outputs'],
 classifiers = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows',
  'Programming Language :: Python',
  'License :: OSI Approved :: MIT License',
'Topic :: Adaptive Technologies',
]
)
