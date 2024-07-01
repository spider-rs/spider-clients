import importlib, requests

class Supabase:
    _client = None

    @staticmethod
    def init():
        if Supabase._client:
            return
        
        Supabase._initialize_client()

    @staticmethod
    def _initialize_client():
        try:
            supabase_module = importlib.import_module('supabase')
            create_client = getattr(supabase_module, 'create_client')
        except ImportError:
            raise ImportError("Supabase client is not available. Install it using 'pip install supabase'")

        response = requests.get("https://api.spider.cloud/data/anon_key")
        if not response.ok:
            raise Exception(f"Failed to fetch anon key: {response.status_code}")

        data = response.json().get('data')
        if not data:
            raise Exception("Anon key data is missing in the response")

        Supabase._client = create_client(
            "https://api-data.spider.cloud",
            str(data)
        )

    @staticmethod
    def get_client():
        if not Supabase._client:
            raise Exception("Supabase client is not initialized. Call Supabase.init() first.")
        return Supabase._client