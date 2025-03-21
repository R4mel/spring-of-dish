import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx"; // 원래 이름(MyApp)이 아니어도 임의로 지정해서 사용 가능

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
