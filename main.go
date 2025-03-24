package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-co-op/gocron"
	"github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

var (
	botToken   = os.Getenv("BOT_TOKEN")
	openaiKey  = os.Getenv("OPENAI_API_KEY")
	userChatID = os.Getenv("USER_CHAT_ID")
	bot        *tgbotapi.BotAPI
)

func sendReminder(text string) {
	id := int64(0)
	fmt.Sscanf(userChatID, "%d", &id)
	msg := tgbotapi.NewMessage(id, text)
	bot.Send(msg)
}

func scheduleReminders() {
	s := gocron.NewScheduler(time.UTC)
	s.Every(1).Day().At("08:00").Do(func() {
		sendReminder("💪 Босс, настало время прокачать спину!\n\n🕘 Утренняя рутина:\n✅ Дыхание\n✅ Мобилизация\n✅ Активация кора\n✅ Растяжка\n\n📹 Видео: https://youtube.com/playlist?list=...")
	})
	s.Every(1).Day().At("23:00").Do(func() {
		sendReminder("🌙 Босс, пора восстановить ось тела!\n\n✅ Осанка\n✅ Копчик-блок\n✅ Растяжка таза\n\n📹 Видео: https://youtube.com/playlist?list=...")
	})
	s.StartAsync()
}

func askGPT(prompt string) string {
	url := "https://api.openai.com/v1/chat/completions"
	payload := map[string]interface{}{
		"model": "gpt-4",
		"messages": []map[string]string{
			{"role": "system", "content": "Ты AI-тренер по восстановлению позвоночника. Отвечай кратко и понятно."},
			{"role": "user", "content": prompt},
		},
	}
	data, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(data))
	req.Header.Add("Authorization", "Bearer "+openaiKey)
	req.Header.Add("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "Ошибка при обращении к AI: " + err.Error()
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	if choices, ok := result["choices"].([]interface{}); ok && len(choices) > 0 {
		msg := choices[0].(map[string]interface{})["message"].(map[string]interface{})["content"].(string)
		return msg
	}
	return "Ответ от AI пустой или нераспознан."
}

func main() {
	var err error
	bot, err = tgbotapi.NewBotAPI(botToken)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Authorized on account %s", bot.Self.UserName)

	scheduleReminders()

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message == nil {
			continue
		}

		text := update.Message.Text
		chatID := update.Message.Chat.ID

		switch text {
		case "/start":
			msg := "Босс, добро пожаловать! Я помогу тебе восстановить спину. Выбирай команду:\n\n📹 Видео\n✅ Отчёт\n📊 Моя фаза\n📖 Все фазы\n❓ Поддержка"
			bot.Send(tgbotapi.NewMessage(chatID, msg))
		case "📹 Видео":
			bot.Send(tgbotapi.NewMessage(chatID, "🕘 Утренняя рутина: https://youtube.com/playlist?list=..."))
			bot.Send(tgbotapi.NewMessage(chatID, "🌙 Вечерняя рутина: https://youtube.com/playlist?list=..."))
		case "📊 Моя фаза":
			bot.Send(tgbotapi.NewMessage(chatID, "Сейчас ты на Фазе 1: Восстановление. Делай ежедневные упражнения 💪"))
		case "📖 Все фазы":
			phases := "🔹 Фаза 1: дыхание, кошка-корова, скрутки...\n🔹 Фаза 2: вакуум, планка, лодочка...\n🔹 Фаза 3: мостик, боковая планка, стоячие упражнения..."
			bot.Send(tgbotapi.NewMessage(chatID, phases))
		case "✅ Отчёт":
			msg := "Отметь, что сделал сегодня:\n✅ Утро\n✅ Вечер\n✅ Копчик-блок\nИ как самочувствие от 1 до 10?"
			bot.Send(tgbotapi.NewMessage(chatID, msg))
		case "❓ Поддержка":
			bot.Send(tgbotapi.NewMessage(chatID, "Напиши вопрос, и я передам его AI-тренеру."))
		default:
			reply := askGPT(text)
			bot.Send(tgbotapi.NewMessage(chatID, "🧠 Тренер ответил:\n"+reply))
		}
	}
}
