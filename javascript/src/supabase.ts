import type { SupabaseClient } from "@supabase/supabase-js";

export class Supabase {
  private static instance?: SupabaseClient;
  private static initPromise?: Promise<void>;

  // Initialize the Supabase client
  static async init(): Promise<void> {
    if (Supabase.instance) {
      return;
    }

    if (Supabase.initPromise) {
      return Supabase.initPromise;
    }

    Supabase.initPromise = (async () => {
      const windowExists = typeof window !== "undefined";
      const { createClient } = await import("@supabase/supabase-js");

      try {
        const response = await fetch("https://api.spider.cloud/data/anon_key");

        if (!response.ok) {
          throw new Error(`Failed to fetch anon key: ${response.statusText}`);
        }

        const { data } = await response.json();

        Supabase.instance = createClient(
          "https://api-data.spider.cloud",
          String(data),
          {
            auth: {
              persistSession: windowExists,
              autoRefreshToken: windowExists,
            },
          }
        );
      } catch (error) {
        Promise.reject("Failed to initialize Supabase client: " + error);
      } finally {
        Supabase.initPromise = undefined; // Clear the init promise
      }
    })();

    return Supabase.initPromise;
  }

  // Get the Supabase client instance
  static get client(): SupabaseClient {
    if (!Supabase.instance) {
      throw new Error(
        "Supabase client is not initialized. Call Supabase.init() first."
      );
    }
    return Supabase.instance;
  }
}
