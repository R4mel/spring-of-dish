import React, { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export default function RedirectPage() {
  const [params] = useSearchParams();
  const code = params.get("code");
  const navigate = useNavigate();

  useEffect(() => {
    if (!code) {
      navigate("/");
      return;
    }
    navigate("/", { replace: true });
  }, [code]);

  return <p>로그인 중</p>;
}