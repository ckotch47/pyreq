import json
import yaml
import httpx
import re
from json import JSONDecodeError

from .resolve_env_in_yaml import load_and_resolve_env


class PyReq:
    def __init__(self, path_to_yaml, path_to_env):
        self.route_config = None
        self.config =  load_and_resolve_env(path_to_yaml, path_to_env)

        self.env = self.config['collection']['environment']
        self.env['variables'] = self.pre_script_run(self.env)
        self.var = self.env['variables']


    def get_header(self, environment, route, var):
        try:
            environment_h = dict(environment.get('headers'))
            for i in environment_h.keys():
                environment_h[i] = environment_h[i].replace(environment_h[i], var[environment_h[i]])
        except:
            environment_h = dict()
        try:
            route_headers = dict(route.get('headers'))
        except:
            route_headers = dict()
        return {**environment_h, **route_headers}

    def pre_script_run(self, collection_settings):
        try:
            var: dict = collection_settings.get('variables')
            pre_script = collection_settings.get('pre_script')
            tmp_i = []
            for v in pre_script:
                if v in tmp_i:
                    continue
                tmp_i.append(v)
                tmp = open(pre_script[v]).read()

                for i in re.findall('\\$_\\w+', tmp):
                    if var[i]:
                        tmp = tmp.replace(i, var[i])
                exec(tmp, globals())

                collection_settings['variables'][v] = pre_request(collection_settings['variables'])
            return collection_settings['variables']
        except KeyError as e:
            print(f'KeyError {e}')
            exit(-1)
        except:
            return collection_settings['variables']

    def replace_url_into_var(self, url):
        try:
            for i in re.findall(r'\$_[a-zA-Z_][a-zA-Z0-9_]*', url):
                url = url.replace(i, self.var[i])
            return url
        except KeyError as e:
            print(f'KeyError {e}')
            exit(-1)
        except Exception as e:
            print(e)
            exit(0)

    def request(self, route_name):
        route_config = self.config['collection'][route_name]

        r = httpx.request(
            method=route_config.get('method'),
            url= self.replace_url_into_var(route_config['url']),
            json=route_config.get('body', {}),
            headers=self.get_header(self.env, route_config, self.var),
            params=route_config.get('query')
        )

        try:
            print(r.status_code)
            print(json.dumps(r.json(), indent=4))
        except JSONDecodeError:
            print(r.status_code, r.text)



def run_req(f, route, e='.env'):
    # TODO добавить везде вывод ошибки если переменная не найдена в енв
    try:
        py_req = PyReq(f, e)
        py_req.request(route)
    except KeyError as e:
        print(f'KeyError {e}')
        exit(-1)
