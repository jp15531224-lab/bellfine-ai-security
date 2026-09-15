export default async (req, context) => {
  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  try {
    const data = await req.json();

    const token = Netlify.env.get("LINE_CHANNEL_ACCESS_TOKEN");
    const userId = Netlify.env.get("LINE_USER_ID");

    if (!token || !userId) {
      return new Response("LINE settings are missing", { status: 500 });
    }

    const text = [
      "【AI防犯カメラ｜新規お問い合わせ】",
      "",
      "■ ご相談内容",
      data["ご相談内容"] || "未入力",
      "",
      "■ 会社名・お名前",
      data["会社名・お名前"] || "未入力",
      "",
      "■ 電話番号",
      data["電話番号"] || "未入力",
      "",
      "■ メールアドレス",
      data["email"] || "未入力",
      "",
      "■ 紹介者名",
      data["紹介者名"] || "未入力",
      "",
      "■ 設置場所・ご要望",
      data["設置場所・ご要望"] || "未入力",
      "",
      "■ 送信日時",
      data["送信日時"] || "未取得"
    ].join("\n");

    const response = await fetch("https://api.line.me/v2/bot/message/push", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        to: userId,
        messages: [
          {
            type: "text",
            text: text
          }
        ]
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("LINE push failed:", response.status, errorText);
      return new Response("LINE notification failed", { status: 500 });
    }

    return new Response("OK", { status: 200 });
  } catch (error) {
    console.error(error);
    return new Response("Server Error", { status: 500 });
  }
};
