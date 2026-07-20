import pytest
from app import app

# 配置测试环境
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'test-secret-key' # 随便设一个密钥用于测试session

@pytest.fixture
def client():
    """创建一个测试客户端"""
    with app.test_client() as client:
        yield client

@pytest.fixture
def logged_in_client(client):
    """模拟已登录的客户端（设置session）"""
    with client.session_transaction() as sess:
        sess['username'] = 'student' # 使用你之前代码里的演示账号
    yield client

#  测试1：/health 返回 200
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['service'] == 'day08-flask-upgrade'

# ✅ 测试2：未登录访问 /api/metrics 被拦截（重定向到登录页）
def test_metrics_unauthorized(client):
    response = client.get('/api/metrics')
    # 根据你的 login_required 逻辑，未登录会返回 302 重定向
    assert response.status_code == 302
    # 检查是否重定向到了登录页
    assert '/login' in response.location

# ✅ 测试3：登录后 /api/metrics 返回 ok 和 metrics
def test_metrics_authorized(logged_in_client):
    response = logged_in_client.get('/api/metrics')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert 'metrics' in data
    assert isinstance(data['metrics'], list)
    # 确保返回的指标里有数据
    if data['metrics']:
        assert 'label' in data['metrics'][0]

# ✅ 测试4：/api/categories?category=Fashion 返回筛选结果
def test_categories_with_filter(logged_in_client):
    response = logged_in_client.get('/api/categories?category=Fashion')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['category'] == 'Fashion'
    assert 'rows' in data
    assert isinstance(data['rows'], list)