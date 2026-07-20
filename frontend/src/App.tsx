import { createContext, FormEvent, ReactNode, useContext, useEffect, useMemo, useState } from "react";
import { Link, Navigate, NavLink, Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  Activity, ArrowRight, BarChart3, BookOpen, Check, ChevronRight, CircleHelp, Clock3,
  FileBarChart, Gauge, Globe2, History, LayoutDashboard, LifeBuoy, LogOut, Mail,
  Menu, PackageOpen, Phone, PieChart, Search, Settings, ShieldCheck, Sparkles,
  UploadCloud, UserRound, WalletCards, X, Zap
} from "lucide-react";
import { Cell, Pie, PieChart as RePieChart, ResponsiveContainer, Tooltip } from "recharts";

import { api, Project, Service, User } from "./api";

type Lang = "en" | "fa";
type Session = { user: User | null; loading: boolean; refresh: () => Promise<void>; logout: () => void };
const SessionContext = createContext<Session>({ user: null, loading: true, refresh: async () => {}, logout: () => {} });
const LanguageContext = createContext<{ lang: Lang; setLang: (lang: Lang) => void }>({ lang: "en", setLang: () => {} });

const copy = {
  en: {
    nav: ["Products", "Solutions", "Resources", "About"], signIn: "Sign in", start: "Start free",
    heroTag: "Analytics that turn transactions into action", hero: "Know your customers. Grow with confidence.",
    heroText: "Upload your commerce data and get clear customer segments, product relationships, purchase scores, and anomaly alerts—in minutes.",
    explore: "Explore products", proof: "Built for commerce teams who need answers, not another complex BI tool.",
    products: "Four powerful ways to understand your business", productsText: "Start with three free analyses. No technical setup and no data-science team required.",
    how: "From spreadsheet to strategy in three steps", about: "Analytics should be useful, not intimidating.",
    aboutText: "InsightFlow is building an accessible analytics layer for growing commerce businesses. We translate raw transaction data into decisions teams can act on.",
    faq: "Questions, answered", contact: "Talk to our team", contactText: "Tell us what you are trying to understand. We will help you choose the right analysis.",
    dashboard: "Dashboard", history: "Analysis history", reports: "Reports", wallet: "Credits & wallet", profile: "Business profile", support: "Support",
  },
  fa: {
    nav: ["محصولات", "راهکارها", "منابع", "درباره ما"], signIn: "ورود", start: "شروع رایگان",
    heroTag: "تحلیل‌هایی که تراکنش را به اقدام تبدیل می‌کنند", hero: "مشتریان خود را بشناسید. با اطمینان رشد کنید.",
    heroText: "داده‌های فروشگاه را بارگذاری کنید و در چند دقیقه بخش‌بندی مشتری، روابط محصولات، امتیاز خرید و هشدارهای ناهنجاری را دریافت کنید.",
    explore: "مشاهده محصولات", proof: "برای تیم‌هایی که پاسخ روشن می‌خواهند، نه یک ابزار پیچیده دیگر.",
    products: "چهار راه قدرتمند برای شناخت بهتر کسب‌وکار", productsText: "با سه تحلیل رایگان شروع کنید؛ بدون تنظیمات فنی و بدون نیاز به تیم علم داده.",
    how: "از فایل داده تا تصمیم در سه مرحله", about: "تحلیل داده باید کاربردی باشد، نه پیچیده.",
    aboutText: "InsightFlow لایه‌ای ساده از تحلیل را برای فروشگاه‌های در حال رشد می‌سازد و داده خام را به تصمیم‌های قابل اجرا تبدیل می‌کند.",
    faq: "پرسش‌های متداول", contact: "با تیم ما صحبت کنید", contactText: "نیاز خود را بگویید تا مناسب‌ترین تحلیل را به شما پیشنهاد کنیم.",
    dashboard: "داشبورد", history: "تاریخچه تحلیل‌ها", reports: "گزارش‌ها", wallet: "اعتبار و کیف پول", profile: "پروفایل کسب‌وکار", support: "پشتیبانی",
  }
};

const productDetails: Record<string, { icon: typeof PieChart; color: string; en: string; fa: string; descEn: string; descFa: string }> = {
  RFM: { icon: PieChart, color: "violet", en: "RFM Segmentation", fa: "بخش‌بندی هوشمند مشتریان", descEn: "Find loyal, new, at-risk, and lost customer groups.", descFa: "مشتریان وفادار، جدید، در معرض ریزش و ازدست‌رفته را پیدا کنید." },
  MARKET_BASKET: { icon: PackageOpen, color: "cyan", en: "Market Basket", fa: "تحلیل سبد خرید", descEn: "Discover products customers naturally buy together.", descFa: "محصولاتی را کشف کنید که مشتریان با هم می‌خرند." },
  PROPENSITY: { icon: Gauge, color: "green", en: "Purchase Propensity", fa: "احتمال خرید", descEn: "Prioritize customers most likely to purchase again.", descFa: "مشتریانی را که احتمال خرید مجدد دارند اولویت‌بندی کنید." },
  ANOMALY: { icon: Activity, color: "orange", en: "Anomaly Detection", fa: "تشخیص ناهنجاری", descEn: "Surface unusual sales and suspicious transactions.", descFa: "فروش‌های غیرعادی و تراکنش‌های مشکوک را شناسایی کنید." }
};

function useLang() { return useContext(LanguageContext); }
function useSession() { return useContext(SessionContext); }

function LanguageToggle() {
  const { lang, setLang } = useLang();
  return <button className="language-toggle" onClick={() => setLang(lang === "en" ? "fa" : "en")}><Globe2 size={16} /> {lang === "en" ? "FA" : "EN"}</button>;
}

function Logo() {
  return <Link to="/" className="logo"><span className="logo-mark"><Sparkles size={19} /></span><span>Insight<span>Flow</span></span></Link>;
}

function AuthModal({ close }: { close: () => void }) {
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("123456");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { refresh } = useSession();
  const navigate = useNavigate();
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      if (step === "phone") { await api.sendOtp(phone); setStep("otp"); }
      else {
        const result = await api.verifyOtp(phone, otp);
        api.tokens.set(result.access_token, result.refresh_token); await refresh(); close(); navigate("/app");
      }
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  };
  return <div className="modal-backdrop" onMouseDown={close}><div className="auth-modal" onMouseDown={e => e.stopPropagation()}>
    <button className="icon-button modal-close" onClick={close}><X size={20} /></button>
    <div className="logo-mark modal-logo"><Sparkles /></div>
    <h2>{step === "phone" ? "Welcome to InsightFlow" : "Check your verification code"}</h2>
    <p>{step === "phone" ? "Enter your mobile number to sign in or create an account." : `We sent a six-digit code to ${phone}.`}</p>
    <form onSubmit={submit}>
      <label>{step === "phone" ? "Mobile number" : "Verification code"}</label>
      <input autoFocus value={step === "phone" ? phone : otp} onChange={e => step === "phone" ? setPhone(e.target.value) : setOtp(e.target.value)} placeholder={step === "phone" ? "09123456789" : "123456"} />
      {error && <div className="form-error">{error}</div>}
      <button className="button primary wide" disabled={busy}>{busy ? "Please wait…" : step === "phone" ? "Continue" : "Verify and continue"}</button>
    </form>
    {step === "otp" && <button className="text-button" onClick={() => setStep("phone")}>Change phone number</button>}
    <small>By continuing, you agree to our Terms and Privacy Policy.</small>
  </div></div>;
}

function Header({ openAuth }: { openAuth: () => void }) {
  const { lang } = useLang(); const t = copy[lang]; const [open, setOpen] = useState(false); const { user } = useSession();
  return <header className="site-header"><div className="container header-inner"><Logo />
    <nav className={open ? "open" : ""}>
      <a href="#products">{t.nav[0]}</a><a href="#solutions">{t.nav[1]}</a><a href="#resources">{t.nav[2]}</a><a href="#about">{t.nav[3]}</a>
    </nav>
    <div className="header-actions"><LanguageToggle />{user ? <Link className="button small primary" to="/app">{t.dashboard}</Link> : <><button className="button small ghost desktop" onClick={openAuth}>{t.signIn}</button><button className="button small primary" onClick={openAuth}>{t.start}</button></>}<button className="icon-button mobile-menu" onClick={() => setOpen(!open)}><Menu /></button></div>
  </div></header>;
}

function LandingPage() {
  const { lang } = useLang(); const t = copy[lang]; const [auth, setAuth] = useState(false); const [services, setServices] = useState<Service[]>([]);
  useEffect(() => { api.services().then(setServices).catch(() => {}); }, []);
  return <><Header openAuth={() => setAuth(true)} /><main>
    <section className="hero"><div className="hero-glow one" /><div className="hero-glow two" /><div className="container hero-grid">
      <div className="hero-copy"><div className="eyebrow"><Zap size={15} />{t.heroTag}</div><h1>{t.hero}</h1><p>{t.heroText}</p><div className="hero-actions"><button className="button primary large" onClick={() => setAuth(true)}>{t.start}<ArrowRight size={18} /></button><a className="button secondary large" href="#products">{t.explore}</a></div><div className="micro-proof"><ShieldCheck size={18} /><span>{t.proof}</span></div></div>
      <div className="hero-visual"><div className="visual-window"><div className="window-top"><i /><i /><i /><span>Customer intelligence overview</span></div><div className="visual-body"><div className="mini-sidebar"><span /><span /><span /><span /></div><div className="mini-content"><div className="mini-heading"><div><small>Revenue intelligence</small><strong>Customer health</strong></div><span>Last 90 days</span></div><div className="metric-row"><div><small>Customers</small><b>12,450</b><em>+14.2%</em></div><div><small>Repeat buyers</small><b>42.7%</b><em>+8.1%</em></div><div><small>At risk</small><b>18.4%</b><em className="warn">Needs action</em></div></div><div className="chart-row"><div className="fake-chart"><div className="bars">{[35,52,44,70,63,82,76,92].map((h,i)=><i key={i} style={{height:`${h}%`}} />)}</div></div><div className="fake-donut"><div className="donut"><span>12.4k<small>customers</small></span></div><div className="legend"><span><i className="loyal"/>Loyal</span><span><i className="risk"/>At risk</span><span><i className="new"/>New</span></div></div></div></div></div></div>
    </div></div></section>
    <section className="trust-strip"><div className="container"><span>Designed for modern commerce</span><div><b>Shopify</b><b>WooCommerce</b><b>Excel</b><b>CSV</b><b>Persian-ready</b></div></div></section>
    <section className="section" id="products"><div className="container"><div className="section-heading centered"><span className="kicker">Analytics suite</span><h2>{t.products}</h2><p>{t.productsText}</p></div><div className="product-grid">
      {(services.filter(s=>s.is_active).length ? services.filter(s=>s.is_active) : Object.keys(productDetails).map(code=>({code,is_active:true} as Service))).map(service => { const p=productDetails[service.code]; if(!p)return null; const Icon=p.icon; return <article className="product-card" key={service.code}><div className={`product-icon ${p.color}`}><Icon /></div><span className="status-pill"><i />Live</span><h3>{lang === "en" ? p.en : p.fa}</h3><p>{lang === "en" ? p.descEn : p.descFa}</p><Link to="/app/products" className="card-link">Learn more <ChevronRight size={16}/></Link></article>; })}
    </div></div></section>
    <section className="section soft" id="solutions"><div className="container"><div className="section-heading centered"><span className="kicker">How it works</span><h2>{t.how}</h2></div><div className="steps"><div><span>01</span><UploadCloud/><h3>Upload securely</h3><p>Drop a CSV or Excel export from your store. Raw files are automatically removed after 48 hours.</p></div><div><span>02</span><Settings/><h3>Map your columns</h3><p>Match your file headers to the required fields with a simple guided mapper.</p></div><div><span>03</span><FileBarChart/><h3>Act on the report</h3><p>Explore clear metrics, ranked opportunities, and downloadable customer-level results.</p></div></div></div></section>
    <section className="section" id="about"><div className="container split-section"><div><span className="kicker">Why InsightFlow</span><h2>{t.about}</h2><p>{t.aboutText}</p><ul className="check-list"><li><Check/>Built for e-commerce operators</li><li><Check/>English and Persian from day one</li><li><Check/>Clear outputs your whole team can use</li><li><Check/>Private, temporary raw-file storage</li></ul></div><div className="quote-card"><Sparkles/><blockquote>“The best analysis is the one your team can understand on Monday and act on by Tuesday.”</blockquote><div><strong>Our product principle</strong><span>Simple inputs. Useful answers.</span></div></div></div></section>
    <section className="section dark" id="resources"><div className="container"><div className="section-heading"><span className="kicker">Built for practical growth</span><h2>One workspace, many decisions.</h2></div><div className="use-grid"><div><BarChart3/><h3>Growth teams</h3><p>Build sharper campaigns with meaningful customer groups and purchase intent.</p></div><div><PackageOpen/><h3>Merchandising</h3><p>Create bundles and cross-sells from real product relationships.</p></div><div><ShieldCheck/><h3>Operations</h3><p>Review unusual sales quickly before they become expensive problems.</p></div></div></div></section>
    <section className="section"><div className="container"><div className="section-heading centered"><span className="kicker">Simple pricing</span><h2>Start free. Scale when value is clear.</h2></div><div className="pricing-card"><div><span>Starter access</span><h3>3 analyses <small>free</small></h3><p>Explore every active engine with your own commerce data.</p></div><ul><li><Check/>All four active products</li><li><Check/>Excel exports</li><li><Check/>Private-beta access</li><li><Check/>No card required</li></ul><button className="button primary large" onClick={()=>setAuth(true)}>Create free account</button></div></div></section>
    <Faq lang={lang}/><ContactSection lang={lang}/><section className="final-cta"><div className="container"><Sparkles/><h2>Turn the data you already have into the growth you want.</h2><p>Start with three free reports. Set up in minutes.</p><button className="button light large" onClick={()=>setAuth(true)}>Start analyzing free <ArrowRight/></button></div></section>
  </main><Footer lang={lang}/>{auth&&<AuthModal close={()=>setAuth(false)}/>}</>;
}

function Faq({lang}:{lang:Lang}) { const t=copy[lang]; const questions=[
  ["What files can I upload?","CSV, XLS, and XLSX transaction exports are supported."],
  ["Do I need a data scientist?","No. The mapper guides your setup and each report is designed for business users."],
  ["How is my data handled?","Raw uploads are removed automatically after 48 hours. Report metadata remains in your private account."],
  ["Which analyses are available?","RFM, Market Basket, Purchase Propensity, and Sales Anomaly Detection are active in the MVP."],
  ["Can I use Persian data?","Yes. Persian headers can be mapped normally and the interface supports full RTL presentation."]
]; const [open,setOpen]=useState(0); return <section className="section soft"><div className="container faq-layout"><div><span className="kicker">FAQ</span><h2>{t.faq}</h2><p>Everything you need to know before your first analysis.</p></div><div>{questions.map((q,i)=><div className={`faq-item ${open===i?"open":""}`} key={q[0]}><button onClick={()=>setOpen(open===i?-1:i)}><span>{q[0]}</span><span>{open===i?"−":"+"}</span></button>{open===i&&<p>{q[1]}</p>}</div>)}</div></div></section>; }

function ContactSection({lang}:{lang:Lang}) { const t=copy[lang]; const [sent,setSent]=useState(false); const [error,setError]=useState(""); const submit=async(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();const f=new FormData(e.currentTarget);try{await api.contact(Object.fromEntries(f) as Record<string,string>);setSent(true)}catch(x){setError((x as Error).message)}}; return <section className="section" id="contact"><div className="container contact-grid"><div><span className="kicker">Contact</span><h2>{t.contact}</h2><p>{t.contactText}</p><div className="contact-points"><span><Mail/>hello@insightflow.ai</span><span><Phone/>Sales and onboarding support</span></div></div>{sent?<div className="success-box"><Check/><h3>Message received</h3><p>Our team will get back to you shortly.</p></div>:<form className="contact-form" onSubmit={submit}><div className="field-row"><input required name="name" placeholder="Your name"/><input required type="email" name="email" placeholder="Work email"/></div><div className="field-row"><input name="company_name" placeholder="Company"/><input name="phone_number" placeholder="Phone (optional)"/></div><input required name="subject" placeholder="How can we help?"/><textarea required name="message" rows={4} placeholder="Tell us a little about your data and goals."/>{error&&<div className="form-error">{error}</div>}<button className="button primary">Send message <ArrowRight size={16}/></button></form>}</div></section>; }

function Footer({lang}:{lang:Lang}) { return <footer><div className="container footer-grid"><div><Logo/><p>Customer intelligence for modern commerce.</p></div><div><b>Product</b><a href="#products">Analytics suite</a><a href="#solutions">How it works</a><Link to="/app">Dashboard</Link></div><div><b>Company</b><a href="#about">About</a><a href="#contact">Contact</a><a href="#resources">Resources</a></div><div><b>Legal</b><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Data policy</a></div></div><div className="container footer-bottom"><span>© 2026 InsightFlow. All rights reserved.</span><LanguageToggle/></div></footer>; }

function Protected({children}:{children:ReactNode}) { const {user,loading}=useSession(); if(loading)return <div className="page-loader"><Sparkles/><span>Loading workspace…</span></div>; return user?<>{children}</>:<Navigate to="/" replace/>; }

const navItems=[
  ["/app",LayoutDashboard,"dashboard"],["/app/products",Sparkles,"Products"],["/app/history",History,"history"],["/app/reports",FileBarChart,"reports"],["/app/wallet",WalletCards,"wallet"],["/app/profile",UserRound,"profile"],["/app/support",LifeBuoy,"support"]
] as const;

function DashboardShell() { const {lang}=useLang(); const t=copy[lang]; const {user,logout}=useSession(); const [mobile,setMobile]=useState(false); return <div className="app-shell"><aside className={mobile?"app-sidebar open":"app-sidebar"}><div className="sidebar-head"><Logo/><button className="icon-button mobile-menu" onClick={()=>setMobile(false)}><X/></button></div><nav>{navItems.map(([to,Icon,label])=><NavLink end={to==="/app"} to={to} key={to} onClick={()=>setMobile(false)}><Icon size={19}/><span>{label in t?t[label as keyof typeof t]:label}</span></NavLink>)}</nav><div className="sidebar-help"><CircleHelp/><strong>Need a hand?</strong><p>Our team can help map your first dataset.</p><Link to="/app/support">Contact support</Link></div><button className="logout" onClick={logout}><LogOut size={18}/>Sign out</button></aside><div className="app-main"><header className="app-header"><button className="icon-button mobile-menu" onClick={()=>setMobile(true)}><Menu/></button><div className="search"><Search size={18}/><input placeholder="Search projects and reports…"/></div><div className="app-header-actions"><LanguageToggle/><div className="credit-chip"><Zap size={15}/>{user?.credit_limit} credits</div><Link to="/app/profile" className="avatar">{user?.company_name?.[0]??user?.phone_number.slice(-2)}</Link></div></header><div className="app-content"><Routes><Route index element={<DashboardHome/>}/><Route path="products" element={<ProductsPage/>}/><Route path="history" element={<HistoryPage reportsOnly={false}/>}/><Route path="reports" element={<HistoryPage reportsOnly/>}/><Route path="wallet" element={<WalletPage/>}/><Route path="profile" element={<ProfilePage/>}/><Route path="support" element={<SupportPage/>}/><Route path="run/:code" element={<RunAnalysisPage/>}/><Route path="report/:id/:type" element={<ReportPage/>}/></Routes></div></div></div>; }

function DashboardHome() { const {user}=useSession(); const [data,setData]=useState<any>(); useEffect(()=>{api.dashboard().then(setData)},[]); return <><div className="page-title"><div><span className="kicker">Workspace overview</span><h1>Good to see you{user?.company_name?`, ${user.company_name}`:""}.</h1><p>Here is what is happening across your customer analytics.</p></div><Link to="/app/products" className="button primary"><Sparkles size={17}/>New analysis</Link></div><div className="stat-grid"><Stat icon={WalletCards} label="Credits remaining" value={data?.credits_remaining??"—"} tone="violet"/><Stat icon={FileBarChart} label="Completed reports" value={data?.successful_projects??"—"} tone="green"/><Stat icon={Clock3} label="Processing" value={data?.processing_projects??"—"} tone="cyan"/><Stat icon={Activity} label="Total analyses" value={data?.total_projects??"—"} tone="orange"/></div><div className="dashboard-grid"><section className="panel wide-panel"><div className="panel-head"><div><h3>Recent activity</h3><p>Your latest analytics projects</p></div><Link to="/app/history">View all <ChevronRight size={16}/></Link></div><ProjectTable projects={data?.recent_projects??[]}/></section><section className="panel quick-panel"><div className="panel-head"><div><h3>Quick start</h3><p>Choose an active engine</p></div></div>{Object.entries(productDetails).map(([code,p])=>{const Icon=p.icon;return <Link key={code} to={`/app/run/${code}`}><span className={`product-icon tiny ${p.color}`}><Icon/></span><span><b>{p.en}</b><small>{p.descEn}</small></span><ChevronRight/></Link>})}</section></div></>; }

function Stat({icon:Icon,label,value,tone}:{icon:any;label:string;value:any;tone:string}) { return <div className="stat-card"><span className={`product-icon ${tone}`}><Icon/></span><div><small>{label}</small><strong>{value}</strong></div></div>; }

function ProjectTable({projects}:{projects:Project[]}) { if(!projects.length)return <div className="empty"><History/><h3>No analyses yet</h3><p>Your completed and active projects will appear here.</p></div>; return <div className="project-table">{projects.map(p=><div className="project-row" key={p.id}><span className={`product-icon tiny ${productDetails[p.analysis_type]?.color??"violet"}`}>{productDetails[p.analysis_type]&&(()=>{const I=productDetails[p.analysis_type].icon;return <I/>})()}</span><div className="project-name"><b>{p.title}</b><small>{p.service_name_en}</small></div><span className={`project-status ${p.status.toLowerCase()}`}><i/>{p.status}</span><time>{new Date(p.created_at).toLocaleDateString()}</time>{p.has_report?<Link to={`/app/report/${p.id}/${p.analysis_type}`} className="icon-button"><ChevronRight/></Link>:<span/>}</div>)}</div>; }

function ProductsPage() { const [services,setServices]=useState<Service[]>([]); useEffect(()=>{api.services().then(setServices)},[]); return <><div className="page-title"><div><span className="kicker">Product catalog</span><h1>Choose your next analysis</h1><p>Turn one transaction file into a focused business answer.</p></div></div><div className="catalog-grid">{services.map(s=>{const p=productDetails[s.code]??{icon:Sparkles,color:"violet",en:s.name_en,descEn:"Join the private beta for early access."};const Icon=p.icon;return <article className="catalog-card" key={s.code}><div className="catalog-top"><span className={`product-icon ${p.color}`}><Icon/></span><span className={s.is_active?"status-pill":"status-pill soon"}><i/>{s.is_active?"Active":"Private beta"}</span></div><h3>{s.name_en}</h3><p>{p.descEn}</p><div className="mapping-count">{s.required_mapping_fields.length||"Custom"} required fields</div><Link className={`button ${s.is_active?"primary":"secondary"}`} to={`/app/run/${s.code}`}>{s.is_active?"Start analysis":"Request access"}<ArrowRight size={16}/></Link></article>})}</div></>; }

function HistoryPage({reportsOnly}:{reportsOnly:boolean}) { const [projects,setProjects]=useState<Project[]>([]); const [query,setQuery]=useState(""); useEffect(()=>{api.projects().then(setProjects)},[]); const shown=projects.filter(p=>(!reportsOnly||p.has_report)&&(`${p.title} ${p.service_name_en}`.toLowerCase().includes(query.toLowerCase())));return <><div className="page-title"><div><span className="kicker">{reportsOnly?"Report library":"Audit trail"}</span><h1>{reportsOnly?"Reports":"Analysis history"}</h1><p>{reportsOnly?"Open and download every completed insight.":"Track every project from upload to result."}</p></div></div><section className="panel"><div className="table-tools"><div className="search"><Search/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search analyses…"/></div><span>{shown.length} projects</span></div><ProjectTable projects={shown}/></section></>; }

function RunAnalysisPage() { const {code="RFM"}=useParams(); const navigate=useNavigate(); const [services,setServices]=useState<Service[]>([]); const [project,setProject]=useState<{id:string;columns:string[]}|null>(null); const [mapping,setMapping]=useState<Record<string,string>>({}); const [busy,setBusy]=useState(false); const [message,setMessage]=useState(""); const service=services.find(s=>s.code===code); useEffect(()=>{api.services().then(setServices)},[]); const upload=async(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();setBusy(true);setMessage("");try{const form=new FormData(e.currentTarget);form.set("analysis_type",code);const r=await api.upload(form);setProject({id:r.project_id,columns:r.detected_columns})}catch(x){setMessage((x as Error).message)}finally{setBusy(false)}}; const submit=async()=>{if(!project||!service)return;setBusy(true);try{if(!service.is_active){await api.waitlist(project.id);setMessage("You are on the private-beta list. Our team will contact you shortly.");return}await api.start(project.id,Object.fromEntries([...service.required_mapping_fields,...service.optional_mapping_fields].map(k=>[k,mapping[k]||null])));navigate("/app/history")}catch(x){setMessage((x as Error).message)}finally{setBusy(false)}}; return <><div className="page-title"><div><span className="kicker">Guided analysis</span><h1>{service?.name_en??productDetails[code]?.en}</h1><p>{service?.is_active?"Upload your data, map its columns, and start the engine.":"Complete the data-fit check to request private-beta access."}</p></div></div><div className="run-layout"><section className="panel"><div className="step-head"><span>1</span><div><h3>Upload transaction data</h3><p>CSV, XLS, or XLSX. Raw files expire after 48 hours.</p></div></div>{!project?<form className="upload-zone" onSubmit={upload}><UploadCloud/><h3>Choose your source file</h3><p>Maximum processing quality starts with clear column headers.</p><input required type="file" name="file" accept=".csv,.xls,.xlsx"/><input required name="title" placeholder="Project title, e.g. Spring campaign"/><button className="button primary" disabled={busy}>{busy?"Uploading…":"Upload and detect columns"}</button></form>:<div className="uploaded"><Check/><div><b>File uploaded successfully</b><span>{project.columns.length} columns detected</span></div></div>}</section>{project&&service&&<section className="panel"><div className="step-head"><span>2</span><div><h3>Map your columns</h3><p>Tell the engine what each source column represents.</p></div></div><div className="mapper">{[...service.required_mapping_fields,...service.optional_mapping_fields].map(field=><label key={field}><span>{field.replaceAll("_"," ")} {service.required_mapping_fields.includes(field)&&<b>*</b>}</span><select value={mapping[field]??""} onChange={e=>setMapping({...mapping,[field]:e.target.value})}><option value="">Not mapped</option>{project.columns.map(c=><option key={c}>{c}</option>)}</select></label>)}</div><button className="button primary" disabled={busy||service.required_mapping_fields.some(f=>!mapping[f])} onClick={submit}>{busy?"Submitting…":service.is_active?"Run analysis":"Join private beta"}<ArrowRight/></button></section>}</div>{message&&<div className="notice">{message}</div>}</>; }

function ReportPage() { const {id="",type=""}=useParams(); const [report,setReport]=useState<any>(); const [error,setError]=useState(""); useEffect(()=>{api.report(id,type).then(setReport).catch(e=>setError(e.message))},[id,type]); if(error)return <div className="notice error">{error}</div>; if(!report)return <div className="page-loader inline"><Sparkles/><span>Loading report…</span></div>; const chart=report.chart_data??[]; return <><div className="page-title"><div><span className="kicker">Completed report</span><h1>{productDetails[type]?.en??type}</h1><p>Generated insight for project {id.slice(0,8)}.</p></div>{(report.download_excel_url||report.summary?.result_file_path)&&<a className="button secondary" href={`/media/${report.download_excel_url??report.summary.result_file_path}`}>Download Excel</a>}</div>{report.summary&&<div className="stat-grid">{Object.entries(report.summary).filter(([k])=>!k.includes("path")).map(([k,v],i)=><Stat key={k} icon={[UserRound,Activity,Gauge,BarChart3][i%4]} label={k.replaceAll("_"," ")} value={v as any} tone={["violet","green","cyan","orange"][i%4]}/>)}</div>}{chart.length>0&&<section className="panel report-chart"><div><h3>Customer segments</h3><p>Distribution across the analyzed customer base</p></div><ResponsiveContainer width="100%" height={320}><RePieChart><Pie data={chart} dataKey="count" nameKey="segment" innerRadius={75} outerRadius={115} paddingAngle={3}>{chart.map((_:any,i:number)=><Cell key={i} fill={["#725cff","#20c997","#46b8e9","#ff9f43","#a78bfa"][i%5]}/>)}</Pie><Tooltip/></RePieChart></ResponsiveContainer></section>}<section className="panel"><div className="panel-head"><div><h3>Detailed output</h3><p>Highest-priority records from this analysis</p></div></div><pre className="json-report">{JSON.stringify(report.rules??report.scores??report.anomalies_list??report.chart_data, null, 2)}</pre></section></>; }

function WalletPage() { const {user}=useSession(); return <><div className="page-title"><div><span className="kicker">Usage</span><h1>Credits & wallet</h1><p>Keep track of your available analytics capacity.</p></div></div><div className="wallet-hero"><div><span>Available balance</span><strong>{user?.credit_limit??0}</strong><small>analysis credits</small></div><div className="wallet-art"><WalletCards/></div></div><div className="dashboard-grid"><section className="panel"><h3>How credits work</h3><ul className="check-list"><li><Check/>One successful queue submission uses one credit</li><li><Check/>File upload and mapping are always free</li><li><Check/>Private-beta requests do not use credits</li><li><Check/>Your first three credits are included</li></ul></section><section className="panel"><h3>Need more capacity?</h3><p>Usage-based plans and team workspaces are coming soon. Contact our team for early access.</p><Link className="button primary" to="/app/support">Talk to sales</Link></section></div></>; }

function ProfilePage() { const {user,refresh}=useSession(); const [message,setMessage]=useState(""); const submit=async(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();const f=new FormData(e.currentTarget);try{await api.updateProfile({company_name:String(f.get("company_name")),industry:String(f.get("industry")),platform:String(f.get("platform"))});await refresh();setMessage("Profile updated successfully.")}catch(x){setMessage((x as Error).message)}};return <><div className="page-title"><div><span className="kicker">Account settings</span><h1>Business profile</h1><p>Keep your account and business context up to date.</p></div></div><section className="panel profile-panel"><div className="profile-banner"><div className="large-avatar">{user?.company_name?.[0]??"I"}</div><div><h3>{user?.company_name??"Your business"}</h3><p>{user?.phone_number}</p></div></div><form className="profile-form" onSubmit={submit}><label>Phone number<input disabled value={user?.phone_number??""}/></label><label>Company name<input required name="company_name" defaultValue={user?.company_name??""}/></label><label>Industry<input required name="industry" defaultValue={user?.industry??""} placeholder="Fashion, electronics, beauty…"/></label><label>Commerce platform<input required name="platform" defaultValue={user?.platform??""} placeholder="Shopify, WooCommerce…"/></label><button className="button primary">Save changes</button>{message&&<span className="form-message">{message}</span>}</form></section></>; }

function SupportPage() { const [sent,setSent]=useState(false); const submit=async(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();const f=new FormData(e.currentTarget);await api.contact(Object.fromEntries(f) as Record<string,string>);setSent(true)}; return <><div className="page-title"><div><span className="kicker">Customer care</span><h1>How can we help?</h1><p>Get help with data mapping, reports, or your account.</p></div></div><div className="dashboard-grid"><section className="panel support-options"><div><BookOpen/><h3>Read the guides</h3><p>Learn how each engine works and prepare clean data.</p></div><div><Mail/><h3>Email support</h3><p>Our team responds to MVP customers directly.</p></div><div><CircleHelp/><h3>Mapping review</h3><p>Ask us to review your columns before spending a credit.</p></div></section><section className="panel">{sent?<div className="success-box"><Check/><h3>Request received</h3></div>:<form className="contact-form" onSubmit={submit}><input required name="name" placeholder="Your name"/><input required type="email" name="email" placeholder="Email"/><input required name="subject" placeholder="Subject"/><textarea required name="message" rows={5} placeholder="Describe what you need help with."/><button className="button primary">Send request</button></form>}</section></div></>; }

export default function App() {
  const [lang,setLangState]=useState<Lang>(()=>(localStorage.getItem("lang") as Lang)||"en");
  const [user,setUser]=useState<User|null>(null); const [loading,setLoading]=useState(true);
  const refresh=async()=>{try{setUser(await api.profile())}catch{setUser(null)}finally{setLoading(false)}};
  useEffect(()=>{refresh()},[]); useEffect(()=>{document.documentElement.lang=lang;document.documentElement.dir=lang==="fa"?"rtl":"ltr";localStorage.setItem("lang",lang)},[lang]);
  const session=useMemo(()=>({user,loading,refresh,logout:()=>{api.tokens.clear();setUser(null)}}),[user,loading]);
  return <LanguageContext.Provider value={{lang,setLang:setLangState}}><SessionContext.Provider value={session}><Routes><Route path="/*" element={<LandingPage/>}/><Route path="/app/*" element={<Protected><DashboardShell/></Protected>}/></Routes></SessionContext.Provider></LanguageContext.Provider>;
}
