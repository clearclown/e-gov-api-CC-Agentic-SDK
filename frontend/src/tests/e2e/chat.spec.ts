import { test, expect } from "@playwright/test";

test.describe("Chat Interface", () => {
  test("should display the chat interface", async ({ page }) => {
    await page.goto("/");

    // Check for main heading
    await expect(page.locator("h1")).toContainText("e-gov 法律相談 AI");

    // Check for chat card
    await expect(page.locator("text=法律相談 AI チャット")).toBeVisible();

    // Check for input field
    await expect(page.locator('input[placeholder="メッセージを入力..."]')).toBeVisible();

    // Check for send button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("should display welcome message when no messages", async ({ page }) => {
    await page.goto("/");

    // Check for welcome message
    await expect(page.locator("text=こんにちは！")).toBeVisible();
    await expect(page.locator("text=法律に関する質問があればお聞きください。")).toBeVisible();
  });

  test("should enable send button when input has text", async ({ page }) => {
    await page.goto("/");

    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Initially, send button should be disabled
    await expect(sendButton).toBeDisabled();

    // Type a message
    await input.fill("テストメッセージ");

    // Send button should now be enabled
    await expect(sendButton).toBeEnabled();
  });
});

test.describe("Multi-LLM Provider Support", () => {
  test("should display LLM provider selector", async ({ page }) => {
    await page.goto("/");

    // Check for provider selector label
    await expect(page.locator("text=LLMプロバイダー:")).toBeVisible();

    // Check for provider dropdown
    const providerSelect = page.locator('select#llm-provider');
    await expect(providerSelect).toBeVisible();
  });

  test("should have all three provider options", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');

    // Check that all three options exist
    await expect(providerSelect.locator('option[value="anthropic"]')).toBeVisible();
    await expect(providerSelect.locator('option[value="deepseek"]')).toBeVisible();
    await expect(providerSelect.locator('option[value="gemini"]')).toBeVisible();

    // Check option labels
    await expect(providerSelect.locator('option[value="anthropic"]')).toHaveText("Anthropic Claude");
    await expect(providerSelect.locator('option[value="deepseek"]')).toHaveText("DeepSeek AI");
    await expect(providerSelect.locator('option[value="gemini"]')).toHaveText("Google Gemini");
  });

  test("should default to Anthropic provider", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');

    // Check that Anthropic is selected by default
    await expect(providerSelect).toHaveValue("anthropic");
  });

  test("should allow switching between providers", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');

    // Switch to DeepSeek
    await providerSelect.selectOption("deepseek");
    await expect(providerSelect).toHaveValue("deepseek");

    // Switch to Gemini
    await providerSelect.selectOption("gemini");
    await expect(providerSelect).toHaveValue("gemini");

    // Switch back to Anthropic
    await providerSelect.selectOption("anthropic");
    await expect(providerSelect).toHaveValue("anthropic");
  });

  test("should disable provider selector while loading", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');
    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Initially, provider selector should be enabled
    await expect(providerSelect).toBeEnabled();

    // Type a message
    await input.fill("テストメッセージ");

    // Mock slow API response to test loading state
    await page.route('**/api/v1/agent/chat', async (route) => {
      // Delay response to simulate loading
      await page.waitForTimeout(2000);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ type: 'text', content: 'Test response' }),
      });
    });

    // Click send button
    await sendButton.click();

    // Provider selector should be disabled during loading
    await expect(providerSelect).toBeDisabled();
  });
});

test.describe("Provider-Specific Functionality", () => {
  test("should create session with Anthropic provider", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');
    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Select Anthropic
    await providerSelect.selectOption("anthropic");

    // Type a message
    await input.fill("労働法について教えてください");

    // Mock session creation response
    let sessionCreated = false;
    await page.route('**/api/v1/agent/session*', async (route) => {
      sessionCreated = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ session_id: 'anthropic-test-session' }),
      });
    });

    // Send message
    await sendButton.click();

    // Wait a moment for session creation
    await page.waitForTimeout(500);

    // Verify session was created
    expect(sessionCreated).toBe(true);
  });

  test("should create session with DeepSeek provider", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');
    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Select DeepSeek
    await providerSelect.selectOption("deepseek");

    // Type a message
    await input.fill("民法について教えてください");

    // Mock session creation response
    let sessionCreated = false;
    await page.route('**/api/v1/agent/session*', async (route) => {
      sessionCreated = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ session_id: 'deepseek-test-session' }),
      });
    });

    // Send message
    await sendButton.click();

    // Wait a moment for session creation
    await page.waitForTimeout(500);

    // Verify session was created
    expect(sessionCreated).toBe(true);
  });

  test("should create session with Gemini provider", async ({ page }) => {
    await page.goto("/");

    const providerSelect = page.locator('select#llm-provider');
    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Select Gemini
    await providerSelect.selectOption("gemini");

    // Type a message
    await input.fill("刑法について教えてください");

    // Mock session creation response
    let sessionCreated = false;
    await page.route('**/api/v1/agent/session*', async (route) => {
      sessionCreated = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ session_id: 'gemini-test-session' }),
      });
    });

    // Send message
    await sendButton.click();

    // Wait a moment for session creation
    await page.waitForTimeout(500);

    // Verify session was created
    expect(sessionCreated).toBe(true);
  });
});

test.describe("Error Handling", () => {
  test("should display error message when session creation fails", async ({ page }) => {
    await page.goto("/");

    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Mock session creation error
    await page.route('**/api/v1/agent/session*', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Session creation failed' }),
      });
    });

    // Type a message
    await input.fill("テストメッセージ");

    // Send message
    await sendButton.click();

    // Wait for error message
    await page.waitForTimeout(1000);

    // Check for error message (toast or error text)
    // This depends on your error handling implementation
    const errorMessage = page.locator("text=セッションの作成に失敗しました").first();
    await expect(errorMessage).toBeVisible({ timeout: 5000 });
  });

  test("should allow retry after error", async ({ page }) => {
    await page.goto("/");

    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // First attempt fails
    let attemptCount = 0;
    await page.route('**/api/v1/agent/session*', async (route) => {
      attemptCount++;
      if (attemptCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Session creation failed' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ session_id: 'retry-test-session' }),
        });
      }
    });

    // Type a message
    await input.fill("テストメッセージ");

    // First attempt
    await sendButton.click();
    await page.waitForTimeout(1000);

    // Clear input and try again
    await input.fill("リトライメッセージ");

    // Second attempt should succeed
    await sendButton.click();

    // Verify second attempt was made
    await page.waitForTimeout(500);
    expect(attemptCount).toBe(2);
  });

  test("should handle API unavailable gracefully", async ({ page }) => {
    await page.goto("/");

    const input = page.locator('input[placeholder="メッセージを入力..."]');
    const sendButton = page.locator('button[type="submit"]');

    // Mock network error
    await page.route('**/api/v1/agent/**', async (route) => {
      await route.abort('failed');
    });

    // Type a message
    await input.fill("テストメッセージ");

    // Send message
    await sendButton.click();

    // Wait for error handling
    await page.waitForTimeout(1000);

    // UI should still be functional (not crashed)
    await expect(input).toBeVisible();
    await expect(sendButton).toBeVisible();
  });
});
