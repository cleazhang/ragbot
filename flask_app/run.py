from app import create_app

app = create_app()

if __name__ == '__main__':
    # 默认端口5050，可以通过环境变量PORT修改
    import os
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=True, port=port, host='0.0.0.0')