import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home.jsx";
import WorldPage from "./pages/WorldPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/world/:id" element={<WorldPage />} />
      </Routes>
    </BrowserRouter>
  );
}
