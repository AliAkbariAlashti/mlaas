import { ComponentType, ReactNode, useEffect, useRef, useState } from "react";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export type ShowcaseVisualProps = { active: boolean };

export type ShowcaseFeature = {
  id: string;
  title: string;
  description: string;
  media?: string;
  mediaAlt?: string;
  link?: string;
  linkLabel?: string;
  visual?: ReactNode;
  customVisual?: ComponentType<ShowcaseVisualProps>;
};

type ScrollFeatureShowcaseProps = {
  features: ShowcaseFeature[];
  id?: string;
  eyebrow?: string;
  title?: string;
  tabs?: ReactNode;
  className?: string;
};

function FeatureMedia({ feature, active }: { feature: ShowcaseFeature; active: boolean }) {
  const [mediaReady, setMediaReady] = useState(false);
  const CustomVisual = feature.customVisual;
  const fallback = feature.visual ?? (CustomVisual ? <CustomVisual active={active} /> : null);
  return <div className="feature-media-content">
    {fallback}
    {feature.media && <img className={mediaReady ? "feature-media-image ready" : "feature-media-image"} src={feature.media} alt={feature.mediaAlt ?? ""} loading="lazy" decoding="async" onLoad={() => setMediaReady(true)} />}
  </div>;
}

export function ScrollFeatureShowcase({ features, id, eyebrow, title, tabs, className = "" }: ScrollFeatureShowcaseProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const itemRefs = useRef<Array<HTMLElement | null>>([]);
  const featureKey = features.map(feature => feature.id).join("|");

  useEffect(() => {
    setActiveIndex(0);
    if (features.length < 2 || typeof IntersectionObserver === "undefined") return;
    const visibleEntries = new Map<Element, IntersectionObserverEntry>();
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.isIntersecting ? visibleEntries.set(entry.target, entry) : visibleEntries.delete(entry.target));
      const visible = Array.from(visibleEntries.values());
      if (!visible.length) return;
      const viewportCenter = window.innerHeight / 2;
      const closest = visible.reduce((best, entry) => {
        const center = entry.boundingClientRect.top + entry.boundingClientRect.height / 2;
        const distance = Math.abs(center - viewportCenter);
        return distance < best.distance ? { entry, distance } : best;
      }, { entry: visible[0], distance: Number.POSITIVE_INFINITY });
      const nextIndex = Number((closest.entry.target as HTMLElement).dataset.featureIndex);
      if (Number.isFinite(nextIndex)) setActiveIndex(nextIndex);
    }, { rootMargin: "-40% 0px -40% 0px", threshold: [0, .15, .35, .6] });

    const items = itemRefs.current;
    items.forEach(item => item && observer.observe(item));
    return () => observer.disconnect();
  }, [featureKey, features.length]);

  if (!features.length) return null;

  return <section className={`scroll-showcase ${className}`.trim()} id={id}>
    <div className="mlf-container">
      {(eyebrow || title) && <header className="showcase-heading">
        {eyebrow && <span>{eyebrow}</span>}
        {title && <h2>{title}</h2>}
      </header>}
      {tabs}
      <div className="showcase-layout">
        <div className="showcase-copy">
          {features.map((feature, index) => <article
            className={index === activeIndex ? "showcase-item active" : "showcase-item"}
            data-feature-index={index}
            key={feature.id}
            ref={node => { itemRefs.current[index] = node; }}
          >
            <span className="showcase-number">{String(index + 1).padStart(2, "0")}</span>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            {feature.link && <Link to={feature.link}>{feature.linkLabel ?? "Learn more"}<ArrowRight /></Link>}
            <div className="showcase-mobile-media"><FeatureMedia feature={feature} active={index === activeIndex} /></div>
          </article>)}
        </div>
        <div className="showcase-sticky" aria-live="polite">
          <div className="showcase-stage">
            {features.map((feature, index) => <div className={index === activeIndex ? "showcase-visual active" : "showcase-visual"} key={feature.id} aria-hidden={index !== activeIndex}>
              <FeatureMedia feature={feature} active={index === activeIndex} />
            </div>)}
          </div>
        </div>
      </div>
    </div>
  </section>;
}
