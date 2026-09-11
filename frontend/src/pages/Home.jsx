import { Link } from "react-router-dom";

export default function Home() {
  return (
    <main className="shell">
      <h1>UNKNOWN</h1>
      <p>Obserwatorium. Świat ogląda się, nie steruje.</p>
      <Link className="ghost" to="/world/1">
        otwórz świat /1
      </Link>
    </main>
  );
}
