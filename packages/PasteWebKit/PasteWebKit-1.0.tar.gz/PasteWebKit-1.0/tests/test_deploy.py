from fixture import *

def test_deploy():
    app = makeapp('test_deploy.ini')
    res = app.get('/')
    assert 'All OK' in res
    assert "'app_config1': 'foo'" in res
    app = makeapp('test_deploy.ini', name='second')
    res = app.get('/')
    assert 'All OK' in res
    assert "'app_config1': 'foo'" in res
    assert "'app_config2': 'bar'" in res

def test_deploy_mult():
    app = makeapp('test_deploy.ini', name='mult')
    res = app.get('/')
    assert "'app_config1': 'foo'" in res
    assert "'app_config2': 'bar'" not in res
    res = app.get('/sec/')
    assert "'app_config2': 'bar'" in res
    
