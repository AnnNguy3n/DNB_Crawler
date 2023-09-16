from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import os
import numpy as np
import re
from linh_tinh import get_df_proxy_by_text_file
from CONFIG import FOLDER_EXTENSION


class EdgeBrowser:
    def __init__(self, number_proxy=-1, random_proxies=True, start_proxy_id=0) -> None:
        '''
        :param number_proxy: -1 hoặc lớn hơn số proxy sẵn có là dùng hết, 0 là không dùng, nếu không thì chọn ngẫu nhiên trong các proxy sẵn có
        '''
        list_proxy = []
        self.list_proxy_infor = []
        list_all_proxy = os.listdir(FOLDER_EXTENSION)
        if number_proxy == -1 or number_proxy > len(list_all_proxy):
            number_proxy = len(list_all_proxy)
            list_proxy = list_all_proxy.copy()
        else:
            if random_proxies:
                list_proxy_id = np.random.choice(np.arange(len(list_all_proxy)), number_proxy, replace=False)
            else:
                list_proxy_id = np.arange(start_proxy_id, start_proxy_id+number_proxy) % len(list_all_proxy)
            list_proxy = [list_all_proxy[_] for _ in list_proxy_id]

        self.number_proxy = number_proxy

        list_proxy.sort()
        list_proxy = [f"{FOLDER_EXTENSION}/{_}" for _ in list_proxy]
        df_proxy = get_df_proxy_by_text_file()
        for proxy in list_proxy:
            proxy_name = re.search(r"proxy_\d+", proxy).group()
            proxy_id = int(proxy_name.split("proxy_")[1])
            host, port, username, password = df_proxy.loc[proxy_id]
            address = f"{username}:{password}@{host}:{port}"
            self.list_proxy_infor.append({
                "name": proxy_name,
                "address": address
            })

        options = webdriver.EdgeOptions()
        options.add_argument("--window-size=1920,1080")
        [options.add_extension(_) for _ in list_proxy]
        self.driver = webdriver.Edge(options=options,
                                     service=Service(EdgeChromiumDriverManager().install()))
        self.driver.get("edge://extensions/")
        if self.number_proxy != 0:
            extension_list = self.driver.find_element(By.ID, "extensions-list")
            list_button = extension_list.find_elements(By.TAG_NAME, "input")
            for button in list_button[1:]:
                button.click()

            self.active_proxy_id = 0
            self.change_proxy(random_proxy=True)

    def change_proxy(self, random_proxy=False):
        self.driver.get("edge://extensions/")
        extension_list = self.driver.find_element(By.ID, "extensions-list")
        list_button = extension_list.find_elements(By.TAG_NAME, "input")
        list_button[self.active_proxy_id].click()
        if random_proxy:
            self.active_proxy_id = np.random.randint(self.number_proxy)
        else:
            self.active_proxy_id += 1
            if self.active_proxy_id == self.number_proxy:
                self.active_proxy_id = 0

        list_button[self.active_proxy_id].click()
