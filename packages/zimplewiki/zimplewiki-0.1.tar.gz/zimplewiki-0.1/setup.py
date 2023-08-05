from setuptools import setup, find_packages

setup(
    name="zimplewiki",
    version="0.1",
    
    packages=find_packages('src'),
    package_dir={"": "src"},
    
    install_requires=["setuptools",
                      "z3c.form",
                      "z3c.formui",
                      "z3c.layer",
                      "z3c.macro",
                      "z3c.template",
                      "zope.viewlet",
                      "zope.app.annotation",
                      "zope.app.zcmlfiles",
                      "zope.app.twisted",
                      "zope.app.securitypolicy",
                      "setuptools_bzr"],
    include_package_data=True,
    zip_safe=False,
    )
