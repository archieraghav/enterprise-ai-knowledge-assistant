import { Mail } from "lucide-react";
import { GithubIcon, LinkedinIcon, TwitterIcon } from "./BrandIcons";

const SOCIAL_LINKS = [
  { Icon: GithubIcon, href: "https://github.com/archieraghav", label: "GitHub" },
  { Icon: LinkedinIcon, href: "https://linkedin.com/in/archie-singh-raghav-a40843272/", label: "LinkedIn" },
  { Icon: TwitterIcon, href: "https://twitter.com/archieraghav02", label: "Twitter" },
];

export default function Footer() {
  return (
    <footer className="border-t border-neutral-200/70 dark:border-neutral-800 mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Archie Singh Raghav</p>
          <p className="text-xs text-neutral-400 dark:text-neutral-500 mt-0.5">
            © {new Date().getFullYear()} Enterprise AI Knowledge Assistant
          </p>
        </div>

        <div className="flex items-center gap-1">
          {SOCIAL_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={link.label}
              className="h-9 w-9 flex items-center justify-center rounded-lg text-neutral-400 dark:text-neutral-500 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            >
              <link.Icon size={17} />
            </a>
          ))}
          <a
            href="mailto:archiesinghraghav@gmail.com"
            aria-label="Email"
            className="h-9 w-9 flex items-center justify-center rounded-lg text-neutral-400 dark:text-neutral-500 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
          >
            <Mail size={17} />
          </a>
        </div>
      </div>
    </footer>
  );
}