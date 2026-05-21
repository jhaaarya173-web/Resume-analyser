from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
DATABASE_URL="mysql+pymysql://2BMSbTaJK5afV85.root:FsM1KMq6kqverCOV@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test"
engine=create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl":{
            "ssl":True

        }
    }
)
sessionLocal=sessionmaker(bind=engine)
base=declarative_base()

