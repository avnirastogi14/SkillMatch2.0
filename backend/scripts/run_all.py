# run_all.py

from load_esco import *
from load_onet import *

load_esco_skills()
load_esco_roles()
load_esco_role_skills()
load_esco_skill_relations()

load_onet_roles()
load_onet_skills()
load_onet_tech_skills()
load_onet_aliases()