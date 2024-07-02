import importlib, requests, os


class Supabase:
    _client = None

    @staticmethod
    def init():
        if Supabase._client is None:
            Supabase._initialize_client()

    @staticmethod
    def _initialize_client():
        try:
            supabase_module = importlib.import_module("supabase")
            create_client = getattr(supabase_module, "create_client")
            client_options = getattr(supabase_module, "ClientOptions")
        except ImportError:
            raise ImportError(
                "Supabase client is not available. Install it using 'pip install supabase'"
            )

        response = requests.get("https://api.spider.cloud/data/anon_key")
        if not response.ok:
            raise Exception(f"Failed to fetch anon key: {response.status_code}")

        data = response.json().get("data")
        if not data:
            raise Exception("Anon key data is missing in the response")

        auto_refresh_token = os.getenv("SUPABASE_AUTO_REFRESH_TOKEN", "True").lower() == "true"

        Supabase._client = create_client(
            "https://api-data.spider.cloud",
            str(data),
            options=client_options(auto_refresh_token=auto_refresh_token),
        )

    @staticmethod
    def get_client():
        if Supabase._client is None:
            raise Exception(
                "Supabase client is not initialized. Call Supabase.init() first."
            )
        return Supabase._client
