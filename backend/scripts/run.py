from load_onet import (
    load_roles,
    load_skills,
    load_knowledge,
    load_technologies,
    load_alternate_titles,
    close_connection
)


def run_onet_pipeline():
    print("🚀 Starting O*NET-only ingestion...\n")

    try:
        load_roles()
        load_skills()
        load_knowledge()
        load_technologies()
        load_alternate_titles()

        print("\nO*NET ingestion completed successfully")

    except Exception as e:
        print("\n❌ ERROR during ingestion:")
        print(e)

    finally:
        close_connection()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    run_onet_pipeline()