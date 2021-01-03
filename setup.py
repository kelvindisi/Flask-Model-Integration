import os

print('checking for required packages')
try:
    import flask
    import jwt
    print('required packages found')
    os.system('python app.py')
except ImportError:
    os.system('pip3 install -r requirements.txt')
    os.system('pip install -U scikit-learn scipy matplotlib')
    print('required packages installed')
    try:
        import flask
        import jwt
        os.system('python app.py')
    except ImportError:
        print("you need to install packages by running pip3 install -r requirements.txt before continuing")