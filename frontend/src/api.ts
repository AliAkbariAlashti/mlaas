export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export type Service = {
  code: string;
  name_en: string;
  name_fa: string;
  is_active: boolean;
  result_kind: "RFM" | "BASKET" | "PREDICTIVE";
  required_mapping_fields: string[];
  optional_mapping_fields: string[];
};

export type Project = {
  id: string;
  title: string;
  analysis_type: string;
  service_name_en: string;
  service_name_fa: string;
  status: "PENDING" | "PROCESSING" | "SUCCESS" | "FAILED" | "WAITLISTED";
  dataset_name: string | null;
  engine_version: string;
  parameters: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  error_log?: string;
  has_report: boolean;
  created_at: string;
};

export type Dataset = {
  id: string; name: string; original_filename: string; file_type: string; file_size: number;
  row_count: number | null; detected_columns: string[];
  validation_status: "PENDING" | "VALID" | "INVALID"; validation_errors: string[];
  runs_count: number; created_at: string; updated_at: string; last_used_at: string | null;
};

export type RunEvent = { id:number; stage:string; message:string; metadata:Record<string,unknown>; created_at:string };

export type User = {
  id: string;
  phone_number: string;
  company_name: string | null;
  industry: string | null;
  platform: string | null;
  credit_limit: number;
  date_joined: string;
  is_profile_complete: boolean;
};

export type NavigationItem = { id:number; title_en:string; title_fa:string; href:string; children:NavigationItem[] };
export type ComponentPage = { slug:string; title_en:string; title_fa:string; description_en:string; description_fa:string; hero_media_url:string };
export type ServiceStep = { title_en:string; title_fa:string; description_en:string; description_fa:string; image_url:string; display_order:number };
export type ProductPage = { slug:string; code:string; is_active:boolean; doc_id:string; title_en:string; title_fa:string; description_en:string; description_fa:string; image_url:string; hero_title_en:string; hero_title_fa:string; hero_media_url:string; get_started_title_en:string; get_started_title_fa:string; steps:ServiceStep[] };
export type DeveloperAPIKey = { id:number; name:string; prefix:string; is_active:boolean; created_at:string; last_used_at:string|null };
export type DeveloperAPIAccess = { plan:string; status:string; monthly_request_limit:number; requests_used:number; requests_remaining:number; period_start:string; period_end:string|null; services:Array<{code:string;name_en:string;name_fa:string;is_active:boolean}>; endpoints:Array<{name:string;path_prefix:string;allow_api_keys:boolean}> };

const tokens = {
  get access() { return localStorage.getItem("access_token"); },
  get refresh() { return localStorage.getItem("refresh_token"); },
  set(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
};

async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (tokens.access) headers.set("Authorization", `Bearer ${tokens.access}`);
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401 && retry && tokens.refresh) {
    const refreshResponse = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh })
    });
    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      localStorage.setItem("access_token", data.access);
      return request<T>(path, options, false);
    }
    tokens.clear();
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const collectMessages = (value: unknown): string[] => {
      if (typeof value === "string") return [value];
      if (Array.isArray(value)) return value.flatMap(collectMessages);
      if (value && typeof value === "object") return Object.values(value).flatMap(collectMessages);
      return [];
    };
    throw new Error(collectMessages(data).join(" ") || "Request failed");
  }
  return data;
}

export const api = {
  tokens,
  sendOtp: (phone_number: string) => request<{ expires_in_seconds: number }>("/auth/send-otp/", { method: "POST", body: JSON.stringify({ phone_number }) }),
  verifyOtp: (phone_number: string, otp_code: string) => request<{ access_token: string; refresh_token: string; is_profile_complete: boolean }>("/auth/verify-otp/", { method: "POST", body: JSON.stringify({ phone_number, otp_code }) }),
  profile: () => request<User>("/user/profile/"),
  updateProfile: (data: Pick<User, "company_name" | "industry" | "platform">) => request("/user/profile/", { method: "PUT", body: JSON.stringify(data) }),
  services: () => request<Service[]>("/services/"),
  dashboard: () => request<any>("/dashboard/"),
  projects: () => request<Project[]>("/projects/"),
  datasets: () => request<Dataset[]>("/datasets/"),
  createDataset: (form: FormData) => request<Dataset>("/datasets/", { method: "POST", body: form }),
  runEvents: (id: string) => request<RunEvent[]>(`/projects/${id}/events/`),
  upload: (form: FormData) => request<{ project_id: string; analysis_type: string; detected_columns: string[] }>("/projects/upload/", { method: "POST", body: form }),
  resume: (id: string) => request<{ project_id: string; analysis_type: string; detected_columns: string[] }>(`/projects/${id}/resume/`),
  start: (id: string, mapping: Record<string, string | null>) => request(`/projects/${id}/start/`, { method: "POST", body: JSON.stringify({ mapping }) }),
  waitlist: (id: string) => request(`/projects/${id}/join-waitlist/`, { method: "POST" }),
  status: (id: string) => request<{ status: Project["status"]; error?: string }>(`/projects/${id}/status/`),
  report: (id: string, type: string) => request<any>(`/projects/${id}/${type === "RFM" ? "rfm-results" : type === "MARKET_BASKET" ? "basket-results" : "predictive-results"}/`),
  blog: () => request<any[]>("/website/blog/"),
  blogPost: (slug: string) => request<any>(`/website/blog/${slug}/`),
  navigation: () => request<NavigationItem[]>("/website/navigation/"),
  components: () => request<ComponentPage[]>("/website/components/"),
  component: (slug: string) => request<ComponentPage>(`/website/components/${slug}/`),
  products: () => request<ProductPage[]>("/website/products/"),
  product: (slug: string) => request<ProductPage>(`/website/products/${slug}/`),
  contact: (data: Record<string, string>) => request("/website/contact/", { method: "POST", body: JSON.stringify(data) }),
  developerAccess: () => request<DeveloperAPIAccess>("/developer/access/"),
  apiKeys: () => request<DeveloperAPIKey[]>("/developer/keys/"),
  createApiKey: (name:string) => request<DeveloperAPIKey & {secret:string}>("/developer/keys/", {method:"POST",body:JSON.stringify({name})}),
  revokeApiKey: (id:number) => request<void>(`/developer/keys/${id}/`, {method:"DELETE"})
};
