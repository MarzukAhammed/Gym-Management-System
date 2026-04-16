// Translation dictionary for English and Bangla
console.log('Translations.js loaded');
const translations = {
  en: {
    "Home": "Home",
    "Explore": "Explore",
    "About Us": "About Us",
    "Video Gallery": "Video Gallery",
    "Gallery": "Gallery",
    "Testimonial": "Testimonial",
    "Contact": "Contact",
    "Language": "Language",
    "English": "English",
    "Bangla": "Bangla",
    "Features": "Features",
    "AI Push-up Counter": "AI Push-up Counter",
    "Diet Plans": "Diet Plans",
    "Progress Tracker": "Progress Tracker",
    "Exercise Library": "Exercise Library",
    "Live Training": "Live Training",
    "Notifications": "Notifications",
    "No new notifications": "No new notifications",
    "View all notifications": "View all notifications",
    "Trainer Profile": "Trainer Profile",
    "Logout": "Logout",
    "Login": "Login",
    "Sign Up": "Sign Up",
    "Platform": "Platform",
    "Trainer Portal": "Trainer Portal",
    "My Profile": "My Profile",
    "Support & Legal": "Support & Legal",
    "Contact Support": "Contact Support",
    "Privacy Policy": "Privacy Policy",
    "Terms & Conditions": "Terms & Conditions",
    "Refund Policy": "Refund Policy",
    "Newsletter": "Newsletter",
    "Get fitness tips and product updates weekly.": "Get fitness tips and product updates weekly.",
    "Subscribe": "Subscribe",
    "Live BD News": "Live BD News"
  },
  bn: {
    "Home": "হোম",
    "Explore": "এক্সপ্লোর",
    "About Us": "আমাদের সম্পর্কে",
    "Video Gallery": "ভিডিও গ্যালারি",
    "Gallery": "গ্যালারি",
    "Testimonial": "রিভিউ",
    "Contact": "যোগাযোগ",
    "Language": "ভাষা",
    "English": "ইংরেজি",
    "Bangla": "বাংলা",
    "Features": "ফিচারসমূহ",
    "AI Push-up Counter": "এআই পুশ-আপ কাউন্টার",
    "Diet Plans": "ডায়েট প্ল্যান",
    "Progress Tracker": "প্রোগ্রেস ট্র্যাকার",
    "Exercise Library": "এক্সারসাইজ লাইব্রেরি",
    "Live Training": "লাইভ ট্রেনিং",
    "Notifications": "নোটিফিকেশন",
    "No new notifications": "নতুন নোটিফিকেশন নেই",
    "View all notifications": "সব নোটিফিকেশন দেখুন",
    "Trainer Profile": "ট্রেইনার প্রোফাইল",
    "Logout": "লগআউট",
    "Login": "লগইন",
    "Sign Up": "সাইন আপ",
    "Platform": "প্ল্যাটফর্ম",
    "Trainer Portal": "ট্রেইনার পোর্টাল",
    "My Profile": "আমার প্রোফাইল",
    "Support & Legal": "সাপোর্ট ও লিগ্যাল",
    "Contact Support": "সাপোর্টে যোগাযোগ",
    "Privacy Policy": "প্রাইভেসি পলিসি",
    "Terms & Conditions": "শর্তাবলী",
    "Refund Policy": "রিফান্ড পলিসি",
    "Newsletter": "নিউজলেটার",
    "Get fitness tips and product updates weekly.": "সাপ্তাহিক ফিটনেস টিপস ও আপডেট পেতে সাবস্ক্রাইব করুন।",
    "Subscribe": "সাবস্ক্রাইব",
    "Live BD News": "লাইভ বিডি নিউজ"
  }
};

function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(';') : [];
  for (let c of cookies) {
    c = c.trim();
    if (c.startsWith(name + '=')) return decodeURIComponent(c.substring(name.length + 1));
  }
  return '';
}

function applyTranslations(lang) {
  const trans = translations[lang] || translations.en;
  console.log('Applying translations for language:', lang);
  
  // Translate elements with data-i18n attribute
  const elements = document.querySelectorAll('[data-i18n]');
  console.log('Found elements with data-i18n:', elements.length);
  elements.forEach(element => {
    const key = element.getAttribute('data-i18n');
    if (key && trans[key]) {
      console.log('Translating:', key, '->', trans[key]);
      element.textContent = trans[key];
    }
  });
}

function initTranslations() {
  const lang = getCookie('django_language') || 'en';
  console.log('Language from cookie:', lang);
  applyTranslations(lang);
}

// Run on page load after everything is ready
window.addEventListener('load', initTranslations);

// Reapply translations after language change
window.addEventListener('languageChanged', function() {
  const lang = getCookie('django_language') || 'en';
  applyTranslations(lang);
});
