export type ErrorLanguage = "en" | "fa";

const persianText = /[\u0600-\u06ff]/;

const translations: Array<[RegExp, string]> = [
  [/cannot assemble with duplicate keys/i, "ستون‌ها یا کلیدهای تکراری در فایل وجود دارد. نام ستون‌ها را یکتا کنید و دوباره تلاش کنید."],
  [/duplicate (column|key|label)/i, "ستون یا کلید تکراری در داده‌ها وجود دارد. نام‌ها باید یکتا باشند."],
  [/only csv,? xls,? and xlsx files are supported/i, "فقط فایل‌های CSV، XLS و XLSX پشتیبانی می‌شوند."],
  [/uploaded file has no header row/i, "فایل بارگذاری‌شده ردیف عنوان ندارد."],
  [/unknown analysis type/i, "نوع تحلیل انتخاب‌شده شناخته‌شده نیست."],
  [/missing_required_fields|missing required field/i, "همه فیلدهای ضروری باید نگاشت شوند."],
  [/anomaly analysis requires at least ten complete transactions/i, "تحلیل ناهنجاری به حداقل ده تراکنش کامل نیاز دارد."],
  [/propensity analysis requires at least four transactions across two customers/i, "تحلیل احتمال خرید به حداقل چهار تراکنش از دو مشتری نیاز دارد."],
  [/analysis service .* is not implemented/i, "این موتور تحلیل هنوز پیاده‌سازی نشده است."],
  [/not included in the api plan/i, "این سرویس در طرح API فعلی شما وجود ندارد."],
  [/only pending projects can be resumed/i, "فقط اجرای در انتظار را می‌توان ادامه داد."],
  [/uploaded source file is no longer available/i, "فایل منبع بارگذاری‌شده دیگر در دسترس نیست."],
  [/available through the private beta waitlist/i, "این سرویس فقط از طریق فهرست انتظار بتای خصوصی در دسترس است."],
  [/project has already been submitted/i, "این اجرا قبلاً ارسال شده است."],
  [/no analysis credits remain/i, "اعتبار پردازش کافی ندارید."],
  [/already available and does not accept beta requests/i, "این سرویس فعال است و درخواست بتا نمی‌پذیرد."],
  [/only pending projects can join the private beta/i, "فقط اجرای در انتظار می‌تواند به بتای خصوصی بپیوندد."],
  [/invalid or expired otp/i, "کد تأیید نامعتبر است یا منقضی شده است."],
  [/all profile fields are required/i, "تکمیل همه فیلدهای پروفایل الزامی است."],
  [/monthly api request limit has been reached/i, "سقف درخواست ماهانه API شما تکمیل شده است."],
  [/no api subscription is assigned/i, "هیچ اشتراک API به حساب شما اختصاص داده نشده است."],
  [/authentication credentials were not provided/i, "برای ادامه باید وارد حساب شوید."],
  [/token.*(invalid|not valid|expired)|invalid token/i, "نشست شما منقضی یا نامعتبر شده است. دوباره وارد شوید."],
  [/not found/i, "منبع درخواستی پیدا نشد."],
  [/permission denied|not permitted|forbidden/i, "اجازه انجام این عملیات را ندارید."],
  [/method .* not allowed/i, "این عملیات در این بخش پشتیبانی نمی‌شود."],
  [/networkerror|failed to fetch|network request failed|econnreset/i, "ارتباط با سرور برقرار نشد. اتصال خود را بررسی و دوباره تلاش کنید."],
  [/this field is required|required/i, "تکمیل فیلدهای ضروری الزامی است."],
  [/invalid date|date.*invalid/i, "یکی از تاریخ‌های فایل نامعتبر است."],
  [/could not convert|string to float|numeric|number/i, "یکی از مقادیر عددی فایل نامعتبر است."],
];

function messageFrom(reason: unknown): string {
  if (reason instanceof Error) return reason.message;
  if (typeof reason === "string") return reason;
  return "Request failed";
}

export function translateError(lang: ErrorLanguage, reason: unknown): string {
  const message = messageFrom(reason).trim();
  if (!message) return "";
  if (lang === "en" || persianText.test(message)) return message;
  return translations.find(([pattern]) => pattern.test(message))?.[1]
    ?? "عملیات انجام نشد. لطفاً داده‌های ورودی را بررسی کرده و دوباره تلاش کنید.";
}
