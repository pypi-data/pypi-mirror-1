from distutils.core import setup, Extension
setup(
        name = 'cztext',
        version = '2.0',
        ext_package='cztext',
        packages = ["cztext"],
        ext_modules = [
            Extension('cztext', ['cztext/cztext.cpp'],
                extra_compile_args=['-O3', '-pipe',
                '-fomit-frame-pointer']),
            ],

        author="zsp",
        author_email="zsp007@gmail.com",
)
