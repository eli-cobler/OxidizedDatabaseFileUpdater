import backup
from services import router_details_service

router_name = input("What is the router_name? ")
router_ip = input("What is the router_ip? ")
username = input("What is the username? ")
password = input("What is the password? ")

#backup.create(router_name, router_ip, username, password)
#backup.get_info('FBC Wagoner', '8c1b099ed6f0.sn.mynetname.net', 'admin', '4EeYd752AV4JvptVA2ky5Hnp')

def run():
    backup_status = backup.create_backup(router_name, router_ip, username, password)
    config_status = backup.create_config(router_name, router_ip, username, password, backup_status)
    router_details_service.get_info(router_name, router_ip, username)
    router_details_service.parse_info(router_name)

if __name__ == "__main__":
    run()