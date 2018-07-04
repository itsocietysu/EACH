class PROVIDER:
    GOOGLE = 'google'
    VK = 'vk'
    FACEBOOK = 'facebook'
    YANDEX = 'yandex'


CONFIG = {
    PROVIDER.GOOGLE: {
        'client_id': '',
        'client_secret': '',
        'realm': '',
        'scope': [],
        'authorization_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://www.googleapis.com/oauth2/v4/token',
        'user_info_url': 'https://www.googleapis.com/plus/v1/people/me',
        'check_token_url': 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token='
    },
    PROVIDER.VK: {
        'client_id': '',
        'client_secret': '',
        'realm': '',
        'scope': [],
        'authorization_url': 'http://api.vkontakte.ru/oauth/authorize',
        'access_token_url': 'https://api.vkontakte.ru/oauth/access_token',
        'user_info_url': 'https://api.vk.com/method/getProfiles?'
                         'fields=uid,first_name,last_name,nickname,sex,bdate,city,country,timezone,photo_big'
    },
    PROVIDER.FACEBOOK: {
        'client_id': '',
        'client_secret': '',
        'realm': '',
        'scope': [],
        'authorization_url': 'https://www.facebook.com/dialog/oauth',
        'access_token_url': 'https://graph.facebook.com/oauth/access_token',
        'user_info_url': 'https://graph.facebook.com/v2.3/me'
    },
    PROVIDER.YANDEX: {
        'client_id': '',
        'client_secret': '',
        'realm': '',
        'scope': [],
        'authorization_url': 'https://oauth.yandex.com/authorize',
        'access_token_url': 'https://oauth.yandex.com/token',
        'user_info_url': 'https://login.yandex.ru/info'
    },
}
