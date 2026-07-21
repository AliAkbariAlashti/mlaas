import { FormEvent, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, BarChart3, Check, Menu, Play, ScanSearch, ShoppingBasket, Target, X } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { Lang, localize, useApp } from "../App";
import { api, Service } from "../api";
import { Brand } from "../components/Brand";
import { ThemeLanguageControls } from "../components/ThemeLanguageControls";
import { translateError } from "../errors";

const fallbackServices = [
  { code: "RFM", name_en: "RFM Segmentation", name_fa: "بخش‌بندی RFM", is_active: true, result_kind: "RFM", required_mapping_fields: [], optional_mapping_fields: [] },
  { code: "MARKET_BASKET", name_en: "Market Basket Analysis", name_fa: "تحلیل سبد خرید", is_active: true, result_kind: "BASKET", required_mapping_fields: [], optional_mapping_fields: [] },
  { code: "PROPENSITY", name_en: "Purchase Propensity", name_fa: "احتمال خرید", is_active: true, result_kind: "PREDICTIVE", required_mapping_fields: [], optional_mapping_fields: [] },
  { code: "ANOMALY", name_en: "Sales Anomaly Detection", name_fa: "تشخیص ناهنجاری فروش", is_active: true, result_kind: "PREDICTIVE", required_mapping_fields: [], optional_mapping_fields: [] }
] as Service[];

const serviceCopy: Record<string, [string, string]> = {
  RFM: ["Group customers by recency, frequency, and value so every retention action has a clear audience.", "مشتریان را بر اساس تازگی، تکرار و ارزش خرید گروه‌بندی کنید تا هر اقدام حفظ مشتری، مخاطب مشخصی داشته باشد."],
  MARKET_BASKET: ["Discover the product combinations that shape baskets and create evidence-led bundles.", "ترکیب محصولاتی را که سبد خرید را شکل می‌دهند کشف کنید و بسته‌های فروش مبتنی بر داده بسازید."],
  PROPENSITY: ["Prioritize the customers most likely to purchase again and focus outreach at the right time.", "مشتریانی را که بیشترین احتمال خرید مجدد دارند اولویت‌بندی کنید و در زمان درست ارتباط بگیرید."],
  ANOMALY: ["Surface unusual transaction patterns early and give operations a focused review queue.", "الگوهای غیرعادی تراکنش را زودتر شناسایی کنید و یک صف بررسی متمرکز در اختیار عملیات قرار دهید."]
};

const fallbackArticles = [
  { slug:"commerce-analytics-foundation", title_en:"From raw data to decisions: building a commerce analytics foundation", title_fa:"از داده خام تا تصمیم: ساخت پایه تحلیل تجارت", excerpt_en:"A practical framework for connecting transaction data to consistent business action.", excerpt_fa:"چارچوبی عملی برای اتصال داده تراکنش به اقدام منسجم کسب‌وکار.", content_en:"Reliable analytics starts with a clear business question, consistent transaction columns, and a repeatable way to turn results into action. Start with one clean export, validate its identifiers and dates, then choose the service that matches the decision your team needs to make.", content_fa:"تحلیل قابل اعتماد با یک پرسش روشن کسب‌وکار، ستون‌های تراکنش منسجم و روشی تکرارپذیر برای تبدیل نتیجه به اقدام آغاز می‌شود.", published_at:"2026-07-12", category_en:"Analytics",category_fa:"تحلیل" },
  { slug:"retention-segments", title_en:"Which customer segments deserve attention first?", title_fa:"کدام بخش‌های مشتری ابتدا به توجه نیاز دارند؟", excerpt_en:"Use recency and repeat behavior to choose a useful retention priority.", excerpt_fa:"با تازگی و تکرار خرید، اولویت مفید حفظ مشتری را انتخاب کنید.", content_en:"Prioritize customers by combining how recently they purchased, how often they return, and the value they create. Give every segment a specific next action.", content_fa:"مشتریان را با ترکیب تازگی خرید، تکرار بازگشت و ارزشی که ایجاد می‌کنند اولویت‌بندی کنید.", published_at:"2026-07-05", category_en:"Retention",category_fa:"حفظ مشتری" },
  { slug:"basket-rules", title_en:"Reading basket rules without overinterpreting them", title_fa:"چگونه قوانین سبد خرید را درست تفسیر کنیم", excerpt_en:"A clear guide to support, confidence, lift, and responsible merchandising.", excerpt_fa:"راهنمای روشن پشتیبانی، اطمینان، لیفت و فروش مسئولانه.", content_en:"Support, confidence, and lift answer different questions. Use all three together before changing bundles or merchandising.", content_fa:"پشتیبانی، اطمینان و لیفت به پرسش‌های متفاوت پاسخ می‌دهند. پیش از تغییر بسته‌ها هر سه معیار را با هم بررسی کنید.", published_at:"2026-06-28", category_en:"Merchandising",category_fa:"فروش" }
];

function Header({ openAuth }: { openAuth: () => void }) {
  const { lang, user } = useApp();
  const [menu, setMenu] = useState(false);
  const nav = [
    ["/products", localize(lang, "Product", "محصول")],
    ["/solutions", localize(lang, "Solutions", "راهکارها")],
    ["/case-studies", localize(lang, "Customers", "مشتریان")],
    ["/blog", localize(lang, "Resources", "منابع")],
    ["/about", localize(lang, "Company", "شرکت")]
  ];
  return <header className="marketing-header"><div className="marketing-container header-row">
    <Brand />
    <nav className={menu ? "nav-open" : ""}>{nav.map(([href, label]) => <Link key={href} to={href} onClick={() => setMenu(false)}>{label}</Link>)}</nav>
    <div className="header-commands"><ThemeLanguageControls compact />{user ? <Link className="button button-solid" to="/app">{localize(lang, "Dashboard", "داشبورد")}</Link> : <><button className="button button-text desktop-action" onClick={openAuth}>{localize(lang, "Sign in", "ورود")}</button><button className="button button-solid" onClick={openAuth}>{localize(lang, "Start free", "شروع رایگان")}</button></>}<button className="menu-button" onClick={() => setMenu(!menu)} aria-label="Menu">{menu ? <X/> : <Menu/>}</button></div>
  </div></header>;
}

function AuthDialog({ close }: { close: () => void }) {
  const { lang, refreshUser } = useApp();
  const [step, setStep] = useState<"phone" | "otp" | "profile">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("123456");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true); setError("");
    try {
      if (step === "phone") { setStep("otp"); await api.sendOtp(phone); }
      else if (step === "otp") { const result = await api.verifyOtp(phone, otp); api.tokens.set(result.access_token, result.refresh_token); if(result.is_profile_complete){await refreshUser();close();navigate("/app")}else setStep("profile"); }
      else { const form=new FormData(event.currentTarget as HTMLFormElement);await api.updateProfile({company_name:String(form.get("company_name")),industry:String(form.get("industry")),platform:String(form.get("platform"))});await refreshUser();close();navigate("/app"); }
    } catch (reason) { setError(translateError(lang, reason)); }
    finally { setBusy(false); }
  };
  return <div className="dialog-backdrop" onMouseDown={close}><div className="auth-dialog" onMouseDown={event => event.stopPropagation()} role="dialog" aria-modal="true">
    <button className="close-button" onClick={close}><X/></button><Brand/>
    <h2>{localize(lang, step === "phone" ? "Sign in to your workspace" : step === "otp" ? "Enter the verification code" : "Tell us about your business", step === "phone" ? "ورود به فضای کاری" : step === "otp" ? "کد تأیید را وارد کنید" : "کسب‌وکار خود را معرفی کنید")}</h2>
    <p>{localize(lang, step === "phone" ? "Use your mobile number to continue. New customers receive three analysis credits." : step === "otp" ? `Enter the MVP code 123456 for ${phone}.` : "Complete these fields once to open your customer dashboard.", step === "phone" ? "برای ادامه شماره موبایل را وارد کنید. مشتریان جدید سه اعتبار تحلیل دریافت می‌کنند." : step === "otp" ? `کد نسخه MVP یعنی 123456 را برای ${phone} وارد کنید.` : "برای ورود به داشبورد مشتری، این اطلاعات را یک‌بار تکمیل کنید.")}</p>
    <form onSubmit={submit}>{step==="profile"?<><input required name="company_name" placeholder={localize(lang,"Company name","نام شرکت")}/><input required name="industry" placeholder={localize(lang,"Industry","صنعت")}/><input required name="platform" placeholder={localize(lang,"Commerce platform","پلتفرم فروش")}/></>:<><label>{localize(lang, step === "phone" ? "Mobile number" : "Verification code", step === "phone" ? "شماره موبایل" : "کد تأیید")}</label><input required inputMode={step==="phone"?"tel":"numeric"} autoFocus value={step === "phone" ? phone : otp} onChange={event => step === "phone" ? setPhone(event.target.value) : setOtp(event.target.value)} placeholder={step === "phone" ? "09123456789" : "123456"}/></>}{error && <span className="form-error" role="alert">{error}</span>}<button className="button button-solid full" disabled={busy}>{busy ? localize(lang, "Please wait…", "لطفاً صبر کنید…") : localize(lang, step === "phone" ? "Send verification code" : step === "otp" ? "Verify and continue" : "Open dashboard", step === "phone" ? "ارسال کد تأیید" : step === "otp" ? "تأیید و ادامه" : "ورود به داشبورد")}</button></form>
    {step === "otp" && <button className="inline-action" onClick={() => {setError("");setStep("phone")}}>{localize(lang, "Change mobile number", "تغییر شماره موبایل")}</button>}
  </div></div>;
}

function ProductPreview({ lang }: { lang: Lang }) {
  return <div className="product-preview" aria-label={localize(lang, "Analytics product preview", "پیش‌نمایش محصول تحلیلی")}>
    <aside><Brand/><span className="preview-nav active">01</span><span className="preview-nav">02</span><span className="preview-nav">03</span><span className="preview-nav">04</span></aside>
    <div className="preview-main"><header><strong>{localize(lang, "Customer segments", "بخش‌های مشتری")}</strong><div><span>{localize(lang, "Overview", "نمای کلی")}</span><span>{localize(lang, "Customers", "مشتریان")}</span><button>{localize(lang, "Export", "خروجی")}</button></div></header>
      <div className="preview-content"><div className="segment-plot"><span className="cluster cluster-one"/><span className="cluster cluster-two"/><span className="cluster cluster-three"/><div className="axis-x"/><div className="axis-y"/><small>{localize(lang, "Purchase frequency", "تکرار خرید")}</small></div><div className="segment-list"><div><i/><span>{localize(lang, "Champions", "برترین‌ها")}</span><b>142</b></div><div><i/><span>{localize(lang, "Loyal", "وفادار")}</span><b>256</b></div><div><i/><span>{localize(lang, "Potential", "مستعد")}</span><b>312</b></div><div><i/><span>{localize(lang, "At risk", "در معرض ریزش")}</span><b>290</b></div></div></div>
      <footer><span>{localize(lang, "Segment logic", "منطق بخش‌بندی")}</span><code>recency · frequency · monetary</code></footer>
    </div>
  </div>;
}

function ServicesCarousel({ services }: { services: Service[] }) {
  const { lang } = useApp();
  const [active, setActive] = useState(0);
  const visible = services.filter(item => item.is_active).slice(0, 4);
  const current = visible[active] ?? fallbackServices[active];
  const move = (direction: number) => setActive(index => (index + direction + visible.length) % visible.length);
  useEffect(() => { const timer = window.setInterval(() => move(1), 7000); return () => window.clearInterval(timer); }, [visible.length]);
  return <section className="services-section" id="services"><div className="marketing-container">
    <div className="section-intro inverse"><h2>{localize(lang, "Analytics that turn data into decisions.", "تحلیل‌هایی که داده را به تصمیم تبدیل می‌کنند.")}</h2><p>{localize(lang, "Four focused services. One clear path from transaction history to the next best action.", "چهار سرویس متمرکز و یک مسیر روشن از تاریخچه تراکنش تا بهترین اقدام بعدی.")}</p></div>
    <div className="service-carousel"><button className="carousel-arrow previous" onClick={() => move(-1)} aria-label="Previous"><ArrowLeft/></button>
      <div className="service-rail">{visible.map((service, index) => <button key={service.code} className={index === active ? "service-slide active" : "service-slide"} onClick={() => setActive(index)}><span>{String(index + 1).padStart(2, "0")}</span><strong>{localize(lang, service.name_en, service.name_fa)}</strong><p>{localize(lang, ...serviceCopy[service.code])}</p>{index === active && <ServiceVisual code={service.code}/>}</button>)}</div>
      <button className="carousel-arrow next" onClick={() => move(1)} aria-label="Next"><ArrowRight/></button>
    </div>
    <div className="carousel-progress"><b>{String(active + 1).padStart(2, "0")}</b><span>/ {String(visible.length).padStart(2, "0")}</span><div>{visible.map((_, index) => <button className={index === active ? "active" : ""} onClick={() => setActive(index)} key={index}/>)}</div><Link to={`/app/run/${current.code}`}>{localize(lang, "Open service", "مشاهده سرویس")}<ArrowRight/></Link></div>
  </div></section>;
}

function ServiceVisual({ code }: { code: string }) {
  if (code === "MARKET_BASKET") return <div className="basket-visual"><div><span>Headphones</span><b>→</b><span>Case</span></div><div><span>Watch</span><b>→</b><span>Strap</span></div><div><span>Laptop</span><b>→</b><span>Hub</span></div></div>;
  if (code === "PROPENSITY") return <div className="bar-visual">{[42,58,35,74,91,63].map((height, index) => <i key={index} style={{height:`${height}%`}}/>)}</div>;
  if (code === "ANOMALY") return <div className="line-visual"><svg viewBox="0 0 300 120"><polyline points="0,82 45,72 90,78 135,45 180,68 225,18 270,61 300,55"/><circle cx="225" cy="18" r="6"/></svg></div>;
  return <div className="matrix-visual">{Array.from({length:35}, (_, index) => <i key={index} style={{opacity:.18 + (index % 6) * .14}}/>)}</div>;
}

function CaseStudy() {
  const { lang } = useApp();
  const steps = [
    ["Challenge", "چالش", "Customer data was spread across exports, making it hard to see who needed attention.", "داده مشتری در فایل‌های مختلف پراکنده بود و تشخیص مشتریان نیازمند توجه دشوار بود."],
    ["Analysis", "تحلیل", "The team mapped one transaction file and used RFM to create understandable customer groups.", "تیم یک فایل تراکنش را نگاشت کرد و با RFM گروه‌های قابل‌فهم مشتری ساخت."],
    ["Action", "اقدام", "Each group received a clear retention priority and an export ready for campaign planning.", "هر گروه یک اولویت حفظ مشتری و خروجی آماده برای برنامه‌ریزی کمپین دریافت کرد."]
  ];
  return <section className="case-study" id="case-study"><div className="marketing-container"><div className="case-title"><span>{localize(lang, "Case study", "مطالعه موردی")}</span><h2>{localize(lang, "From scattered transactions to a clear retention plan.", "از تراکنش‌های پراکنده تا یک برنامه روشن حفظ مشتری.")}</h2><p>{localize(lang, "A practical example of how a commerce team can move from unclear customer behavior to focused action without changing its data stack.", "نمونه‌ای عملی از اینکه یک تیم فروش چگونه بدون تغییر زیرساخت داده، از رفتار مبهم مشتری به اقدام متمرکز می‌رسد.")}</p></div><div className="case-flow">{steps.map((step, index) => <article key={step[0]}><span>{String(index + 1).padStart(2,"0")}</span><div className={`case-graphic graphic-${index + 1}`}>{Array.from({length:index===1?24:8},(_,i)=><i key={i}/>)}</div><h3>{localize(lang, step[0], step[1])}</h3><p>{localize(lang, step[2], step[3])}</p></article>)}</div></div></section>;
}

function Weblog() {
  const { lang } = useApp(); const [posts, setPosts] = useState<any[]>([]);
  useEffect(() => { api.blog().then(setPosts).catch(() => {}); }, []);
  const articles = posts.length ? posts : fallbackArticles;
  const featured = articles[0];
  return <section className="weblog-section" id="weblog"><div className="marketing-container"><div className="weblog-heading"><h2>{localize(lang, "Ideas for better commerce decisions.", "ایده‌هایی برای تصمیم‌های بهتر در تجارت.")}</h2><Link to="/blog">{localize(lang, "Explore all articles", "مشاهده همه نوشته‌ها")}<ArrowRight/></Link></div><div className="featured-article"><div className="editorial-art"><div className="editorial-bars">{[30,48,72,56].map((h,i)=><i key={i} style={{height:`${h}%`}}/>)}</div><svg viewBox="0 0 400 220"><polyline points="10,190 110,140 180,160 260,70 390,35"/></svg><span className="editorial-circle"/></div><article><span>{localize(lang, featured.category_en??"Analytics", featured.category_fa??"تحلیل")}</span><h3>{localize(lang, featured.title_en, featured.title_fa)}</h3><p>{localize(lang, featured.excerpt_en, featured.excerpt_fa)}</p><time>{new Date(featured.published_at).toLocaleDateString(lang === "fa" ? "fa-IR" : "en-US", {year:"numeric",month:"long",day:"numeric"})}</time><Link to={`/blog/${featured.slug}`}>{localize(lang, "Read article", "مطالعه نوشته")}<ArrowRight/></Link></article></div><div className="article-list" id="weblog-list">{articles.slice(1).map((article:any) => <Link className="article-row" to={`/blog/${article.slug}`} key={article.slug}><div className="article-thumb"><span/><i/><i/><i/></div><span>{localize(lang, article.category_en??"Insight", article.category_fa??"بینش")}</span><h3>{localize(lang, article.title_en, article.title_fa)}</h3><p>{localize(lang, article.excerpt_en, article.excerpt_fa)}</p><time>{new Date(article.published_at).toLocaleDateString(lang === "fa" ? "fa-IR" : "en-US")}</time><ArrowRight/></Link>)}</div></div></section>;
}

function ContactFooter({ openAuth }: { openAuth: () => void }) {
  const { lang } = useApp(); const [contact, setContact] = useState(false); const [sent, setSent] = useState(false);
  const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const values = Object.fromEntries(new FormData(event.currentTarget)) as Record<string,string>; await api.contact(values); setSent(true); };
  return <><section className="contact-cta" id="company"><div className="marketing-container"><div><span className="question-mark">?</span><div><h2>{localize(lang, "Bring your hardest customer question.", "سخت‌ترین پرسش مشتری خود را مطرح کنید.")}</h2><p>{localize(lang, "Our team will help you turn complexity into a practical analysis plan.", "تیم ما به شما کمک می‌کند پیچیدگی را به یک برنامه تحلیل عملی تبدیل کنید.")}</p></div></div><div><button className="button button-light" onClick={() => setContact(true)}>{localize(lang, "Talk to our team", "گفتگو با تیم ما")}<ArrowRight/></button><button className="button button-line" onClick={openAuth}>{localize(lang, "Start free", "شروع رایگان")}<ArrowRight/></button></div></div></section>
  <footer className="site-footer"><div className="marketing-container footer-columns"><div><Brand/><p>{localize(lang, "Analytics for commerce teams who want clarity, alignment, and impact.", "تحلیل برای تیم‌های تجاری که وضوح، هماهنگی و اثر می‌خواهند.")}</p></div>{[
    ["Product","محصول",[["Overview","نمای کلی"],["Platform","پلتفرم"],["Services","سرویس‌ها"],["Pricing","قیمت‌گذاری"],["Security","امنیت"]]],
    ["Resources","منابع",[["Weblog","وبلاگ"],["Guides","راهنماها"],["Documentation","مستندات"],["API","رابط برنامه‌نویسی"],["Status","وضعیت"]]],
    ["Company","شرکت",[["About","درباره ما"],["Customers","مشتریان"],["Partners","همکاران"],["Contact","تماس"],["Careers","فرصت‌های شغلی"]]],
    ["Legal","حقوقی",[["Privacy","حریم خصوصی"],["Terms","شرایط استفاده"],["Data processing","پردازش داده"],["Cookies","کوکی‌ها"]]]
  ].map(group => <div key={group[0] as string}><strong>{localize(lang,group[0] as string,group[1] as string)}</strong>{(group[2] as string[][]).map(item=><Link to={({Overview:"/",Platform:"/solutions",Services:"/products",Pricing:"/contact",Security:"/about",Weblog:"/blog",Guides:"/blog",Documentation:"/about",API:"/about",Status:"/contact",About:"/about",Customers:"/case-studies",Partners:"/contact",Contact:"/contact",Careers:"/contact",Privacy:"/about",Terms:"/about","Data processing":"/about",Cookies:"/about"} as Record<string,string>)[item[0]]??"/"} key={item[0]}>{localize(lang,item[0],item[1])}</Link>)}</div>)}</div><div className="marketing-container footer-bottom"><span>© 2026 InsightFlow. {localize(lang,"All rights reserved.","تمام حقوق محفوظ است.")}</span><ThemeLanguageControls/></div></footer>
  {contact && <div className="dialog-backdrop" onMouseDown={() => setContact(false)}><div className="contact-dialog" onMouseDown={e=>e.stopPropagation()}><button className="close-button" onClick={()=>setContact(false)}><X/></button>{sent?<div className="contact-success"><Check/><h3>{localize(lang,"Message received","پیام دریافت شد")}</h3><p>{localize(lang,"We will contact you shortly.","به‌زودی با شما تماس می‌گیریم.")}</p></div>:<form onSubmit={submit}><h2>{localize(lang,"Talk to our team","با تیم ما گفتگو کنید")}</h2><input required name="name" placeholder={localize(lang,"Your name","نام شما")}/><input required type="email" name="email" placeholder={localize(lang,"Work email","ایمیل کاری")}/><input name="company_name" placeholder={localize(lang,"Company","شرکت")}/><input required name="subject" placeholder={localize(lang,"Subject","موضوع")}/><textarea required name="message" rows={5} placeholder={localize(lang,"What would you like to understand?","چه چیزی را می‌خواهید بهتر درک کنید؟")}/><button className="button button-solid full">{localize(lang,"Send message","ارسال پیام")}</button></form>}</div></div>}</>;
}

function WebsitePage({ path, openAuth }: { path:string; openAuth:()=>void }) {
  const {lang}=useApp();const [posts,setPosts]=useState<any[]>(fallbackArticles);const slug=path.startsWith("/blog/")?path.split("/").filter(Boolean)[1]:"";
  useEffect(()=>{if(path==="/blog")api.blog().then(items=>items.length&&setPosts(items)).catch(()=>{});if(slug)api.blogPost(slug).then(item=>setPosts([item])).catch(()=>setPosts(fallbackArticles.filter(item=>item.slug===slug)))},[path,slug]);
  const pageCopy:Record<string,[string,string,string,string]>={
    "/products":["Analytics products","محصولات تحلیلی","Four working engines for customer, basket, propensity, and anomaly analysis.","چهار موتور فعال برای تحلیل مشتری، سبد خرید، احتمال خرید و ناهنجاری."],
    "/solutions":["One workflow, clear decisions","یک جریان کاری، تصمیم‌های روشن","Upload your transaction file, map its columns, run an engine, and receive an actionable report.","فایل تراکنش را بارگذاری و ستون‌ها را نگاشت کنید، موتور را اجرا کنید و گزارش عملی بگیرید."],
    "/case-studies":["Customer outcomes","نتایج مشتریان","See how commerce teams turn scattered transaction data into focused growth actions.","ببینید تیم‌های تجاری چگونه داده پراکنده را به اقدام رشد متمرکز تبدیل می‌کنند."],
    "/about":["Built for practical analytics","ساخته‌شده برای تحلیل عملی","InsightFlow gives commerce teams useful machine-learning reports without requiring an internal data-science team.","InsightFlow بدون نیاز به تیم علم داده داخلی، گزارش‌های یادگیری ماشین کاربردی ارائه می‌دهد."],
    "/contact":["Talk to our team","با تیم ما گفتگو کنید","Tell us about your data and the decision you need to make.","درباره داده و تصمیم مورد نیاز خود با ما صحبت کنید."]
  };
  if(path==="/blog"||slug)return <><Header openAuth={openAuth}/><main className="inner-page"><div className="marketing-container">{slug?(posts.length?posts.map(post=><article className="blog-detail" key={post.slug}><Link to="/blog">← {localize(lang,"All articles","همه نوشته‌ها")}</Link><span>{localize(lang,post.category_en??"Insight",post.category_fa??"بینش")}</span><h1>{localize(lang,post.title_en,post.title_fa)}</h1><p className="lead">{localize(lang,post.excerpt_en,post.excerpt_fa)}</p><div className="article-body">{localize(lang,post.content_en,post.content_fa)}</div></article>):<div className="workspace-empty">{localize(lang,"Article not found.","نوشته پیدا نشد.")}</div>):<><div className="inner-hero"><span>{localize(lang,"Weblog","وبلاگ")}</span><h1>{localize(lang,"Ideas for better commerce decisions.","ایده‌هایی برای تصمیم‌های بهتر در تجارت.")}</h1></div><div className="blog-grid">{posts.map(post=><Link to={`/blog/${post.slug}`} key={post.slug}><BarChart3/><span>{localize(lang,post.category_en??"Insight",post.category_fa??"بینش")}</span><h2>{localize(lang,post.title_en,post.title_fa)}</h2><p>{localize(lang,post.excerpt_en,post.excerpt_fa)}</p><strong>{localize(lang,"Read article","مطالعه نوشته")} <ArrowRight/></strong></Link>)}</div></>}</div></main><ContactFooter openAuth={openAuth}/></>;
  const copy=pageCopy[path]??pageCopy["/about"];
  const cards=path==="/products"?[[BarChart3,"RFM Segmentation","بخش‌بندی RFM"],[ShoppingBasket,"Market Basket","تحلیل سبد خرید"],[Target,"Purchase Propensity","احتمال خرید"],[ScanSearch,"Anomaly Detection","تشخیص ناهنجاری"]]:[[Check,"Upload and validate","بارگذاری و اعتبارسنجی"],[Target,"Map business fields","نگاشت فیلدهای کسب‌وکار"],[BarChart3,"Receive clear reports","دریافت گزارش روشن"]];
  return <><Header openAuth={openAuth}/><main className="inner-page"><div className="marketing-container"><div className="inner-hero"><span>InsightFlow</span><h1>{localize(lang,copy[0],copy[1])}</h1><p>{localize(lang,copy[2],copy[3])}</p><button className="button button-solid large" onClick={openAuth}>{localize(lang,"Open your dashboard","ورود به داشبورد")}</button></div>{path==="/case-studies"?<CaseStudy/>:<div className="feature-grid">{cards.map(([Icon,en,fa])=><article key={en as string}><Icon/><h2>{localize(lang,en as string,fa as string)}</h2><p>{localize(lang,"Designed as a guided, measurable customer workflow.","به‌صورت یک جریان هدایت‌شده و قابل اندازه‌گیری طراحی شده است.")}</p></article>)}</div>}</div></main><ContactFooter openAuth={openAuth}/></>;
}

export function LandingPage() {
  const { lang } = useApp();const {pathname}=useLocation(); const [auth, setAuth] = useState(false); const [services, setServices] = useState<Service[]>(fallbackServices);
  useEffect(() => { api.services().then(result => setServices(result.length ? result : fallbackServices)).catch(() => {}); }, []);
  useEffect(()=>{const elements=[...document.querySelectorAll<HTMLElement>("main section, .inner-hero, .feature-grid>article, .blog-grid>a")];const observer=new IntersectionObserver(entries=>entries.forEach(entry=>entry.isIntersecting&&entry.target.classList.add("revealed")),{threshold:.12});elements.forEach(element=>observer.observe(element));return()=>observer.disconnect()},[pathname]);
  if(pathname!=="/")return <div className="marketing-page"><WebsitePage path={pathname} openAuth={()=>setAuth(true)}/>{auth&&<AuthDialog close={()=>setAuth(false)}/>}</div>;
  return <div className="marketing-page"><Header openAuth={() => setAuth(true)}/><main>
    <section className="hero-section"><div className="blueprint-grid"/><div className="marketing-container hero-layout"><div className="hero-copy"><h1>{localize(lang, "Know your customers. Grow with confidence.", "مشتریان خود را بشناسید. با اطمینان رشد کنید.")}</h1><p>{localize(lang, "Turn transaction data into customer segments, product relationships, purchase scores, and anomaly alerts.", "داده تراکنش را به بخش‌های مشتری، روابط محصول، امتیاز خرید و هشدار ناهنجاری تبدیل کنید.")}</p><div><button className="button button-solid large" onClick={() => setAuth(true)}>{localize(lang,"Start analyzing free","تحلیل رایگان را شروع کنید")}</button><a className="button button-outline large" href="#services"><Play size={16}/>{localize(lang,"Explore the platform","مشاهده پلتفرم")}</a></div></div><ProductPreview lang={lang}/></div><div className="marketing-container next-chapter" id="workflow"><span className="cube-motif"><i/><i/><i/></span><div><h2>{localize(lang,"From raw data to actionable insight","از داده خام تا بینش قابل اجرا")}</h2><p>{localize(lang,"Upload one familiar file, map the columns, and let a focused engine produce a report your team can use.","یک فایل آشنا را بارگذاری کنید، ستون‌ها را نگاشت کنید و گزارشی قابل استفاده برای تیم خود بگیرید.")}</p></div></div></section>
    <ServicesCarousel services={services}/><CaseStudy/><Weblog/><ContactFooter openAuth={() => setAuth(true)}/>
  </main>{auth && <AuthDialog close={() => setAuth(false)}/>}</div>;
}
