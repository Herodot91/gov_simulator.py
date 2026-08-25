import FlorTechSection from "./FlorTechSection.jsx";
import AgroFlorSection from "./AgroFlorSection.jsx";

// FlorTech and AgroFlor -- unlike K-12/lycee schools (a Prefecture/municipal
// education-directorate concern), Moldova's real universities report
// directly to the national Ministry of Education, so these two get their
// own tab rather than sitting under Schools.
export default function UniversitiesTab() {
  return (
    <>
      <p className="caption">
        FlorTech and AgroFlor answer to the national Ministry of Education directly, not the
        Prefecture's own education directorate — their campuses, programs, labs, and other
        infrastructure, browsable here separately from the K-12/lycee schools in the Schools tab.
      </p>
      <FlorTechSection />
      <AgroFlorSection />
    </>
  );
}
