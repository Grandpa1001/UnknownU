import { useParams } from "react-router-dom";
import WorldViewport from "../world/WorldViewport.jsx";

export default function WorldPage() {
  const { id } = useParams();
  return (
    <main className="world-page">
      <WorldViewport worldId={id} />
    </main>
  );
}
