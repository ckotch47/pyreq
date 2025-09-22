import json
import yaml
import httpx
import re
from json import JSONDecodeError

from .resolve_env_in_yaml import load_and_resolve_env


class PyReq:
    def __init__(self, path_to_yaml):
        self.route_config = None
        self.config =  load_and_resolve_env(path_to_yaml)

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
        except:
            return collection_settings['variables']


    def request(self, route_name):
        self.route_config = self.config['collection'][route_name]
        r = httpx.request(
            method=self.route_config.get('method'),
            # TODO find by pattern $_base_url and replace to find into variebles
            url=f"{self.route_config['url'].replace('$_base_url', self.var['$_base_url'])}",
            json=self.route_config.get('body', {}),
            headers=self.get_header(self.env, self.route_config, self.var),
            params=self.route_config.get('query')
        )

        try:
            print(r.status_code)
            print(json.dumps(r.json(), indent=4))
        except JSONDecodeError:
            print(r.status_code, r.text)



def run_req(f, route):
    py_req = PyReq(f)
    py_req.request(route)

