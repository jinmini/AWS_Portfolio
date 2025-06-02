import RootLayout from "@/components/layout/root-layout"
import HeroSection from "@/components/portfolio/hero-section"
import AboutSection from "@/components/portfolio/about-section"
import SkillsSection from "@/components/portfolio/skills-section"
import ProjectsSection from "@/components/portfolio/projects-section"
import ContactSection from "@/components/portfolio/contact-section"

export default function HomePage() {
  return (
    <RootLayout>
      <HeroSection />
      <AboutSection />
      <SkillsSection />
      <ProjectsSection />
      <ContactSection />
    </RootLayout>
  )
} 