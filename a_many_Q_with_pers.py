import openai
import streamlit as st
import time
import re  # Import regular expressions

st.subheader("心语助手")

openai.api_key = st.secrets["OPENAI_API_KEY"]
# openai.base_url = "https://api.openai.com/v1/assistants"
openai.default_headers = {"OpenAI-Beta": "assistants=v2"}

# # client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# client = OpenAI(default_headers={"OpenAI-Beta": "assistants=v2"}, api_key=st.secrets["OPENAI_API_KEY"])
assistant_id = st.secrets["a_many_Q_with_pers"]
print(assistant_id)
speed = 200

min_duration = 2




if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

if "show_thread_id" not in st.session_state:
    st.session_state.show_thread_id = False

if "first_message_sent" not in st.session_state:
    st.session_state.first_message_sent = False

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if 'duration' not in st.session_state:
    st.session_state.duration = 0
    
if 'first_input_time' not in st.session_state:
    st.session_state.first_input_time = None
    
# Automatically send a "hello" message when the chat begins


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)
        

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")
# remaining_time = 1.00 - st.session_state.duration

# if remaining_time > 0:
#     st.sidebar.markdown("##### 1. 请进行至少4轮对话。 \n"
#                         f"##### 2. Thread_id会在<strong><span style='color: #8B0000;'>  {remaining_time:.2f}分钟 </span></strong>之后出现.\n"
#                         , unsafe_allow_html=True)
# else:
#     st.sidebar.markdown("请复制下面的thread_id")
# st.sidebar.info(st.session_state.thread_id)

st.sidebar.markdown("##### 请在这里复制thread_id \n")


def update_typing_animation(placeholder, current_dots):
    """
    Updates the placeholder with the next stage of the typing animation.

    Args:
    placeholder (streamlit.empty): The placeholder object to update with the animation.
    current_dots (int): Current number of dots in the animation.
    """
    num_dots = (current_dots % 6) + 1  # Cycle through 1 to 3 dots
    placeholder.markdown("回答生成中，请等待" + "." * num_dots)
    return num_dots



# Handling message input and response
max_messages = 40  # 10 iterations of conversation (user + assistant)

min_messages = 0


if len(st.session_state.messages) < max_messages:
    
    # if first_input_time is not None, check if the user has been inactive for more than 1 minute
    if st.session_state.first_input_time:
        if time.time() - st.session_state.first_input_time > min_duration * 60:
            st.session_state.show_thread_id = True
            st.sidebar.info(st.session_state.thread_id)
            
        
    
    user_input = st.chat_input("")
    if not st.session_state.first_message_sent:
        
        # insert an image here
        st.image("https://i.ibb.co/dDWxKws/Can-AI-Really-Understand-Human-Emotions-IMG-3.jpg", width=240)
        # st.markdown(
        #     "Start your conversation with the bot.", unsafe_allow_html=True
        # )
    if not st.session_state.first_message_sent:
        st.session_state.first_message_sent = True
        initial_message = "🌟 欢迎来到您的情感陪伴聊天室！我是这里的虚拟助手。无论您是想要分享今天的喜悦，还是需要有人倾听您的心事，我都在这里陪伴您。请随时告诉我您的想法，或者我们可以聊聊您的日常。我们开始吧！🌼"
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        with st.chat_message("assistant"):
            st.markdown(initial_message)

    if user_input:
        if not st.session_state.first_input_time:
            st.session_state.first_input_time = time.time()
        st.session_state.duration = (time.time() - st.session_state.first_input_time) / 60
        remaining_time = min_duration - st.session_state.duration
        if remaining_time > 0:
            st.sidebar.markdown(""
                f"##### Thread_id会在<strong><span style='color: #8B0000;'>  {remaining_time:.2f}分钟 </span></strong>之后出现.\n"
                , unsafe_allow_html=True)
        else:
            st.sidebar.markdown("")
        st.sidebar.caption("请复制thread_id")
        st.session_state.first_message_sent = True
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            waiting_message = st.empty()  # Create a new placeholder for the waiting message
            dots = 0

#------------------------------------------------------------------------------------------------------------------------------#
            def format_response(response):
                """
                Formats the response to handle bullet points and new lines.
                Targets both ordered (e.g., 1., 2.) and unordered (e.g., -, *, •) bullet points.
                """
                # Split the response into lines
                lines = response.split('\n')
                
                formatted_lines = []
                for line in lines:
                    # Check if the line starts with a bullet point (ordered or unordered)
                    if re.match(r'^(\d+\.\s+|[-*•]\s+)', line):
                        formatted_lines.append('\n' + line)
                    else:
                        formatted_lines.append(line)

                # Join the lines back into a single string
                formatted_response = '\n'.join(formatted_lines)

                return formatted_response.strip()
        
            import time
            max_attempts = 2
            attempt = 0
            while attempt < max_attempts:
                try:
                    update_typing_animation(waiting_message, 5)  # Update typing animation
                    # raise Exception("test")
                    message = openai.beta.threads.messages.create(thread_id=st.session_state.thread_id,role="user",content=user_input)
                    run = openai.beta.threads.runs.create(thread_id=st.session_state.thread_id,assistant_id=assistant_id,extra_headers = {"OpenAI-Beta": "assistants=v2"})
                    
                    # Wait until run is complete
                    while True:
                        run_status = openai.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id,run_id=run.id)
                        if run_status.status == "completed":
                            break
                        dots = update_typing_animation(waiting_message, dots)  # Update typing animation
                        time.sleep(0.3) 
                    # Retrieve and display messages
                    messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    full_response = messages.data[0].content[0].text.value
                    full_response = format_response(full_response)  # Format for bullet points
                    chars = list(full_response)
                    # speed = 20  # Display 5 Chinese characters per second
                    delay_per_char = 1.0 / speed
                    displayed_message = ""
                    waiting_message.empty()
                    for char in chars:
                        displayed_message += char
                        message_placeholder.markdown(displayed_message)
                        time.sleep(delay_per_char)  # Wait for calculated delay time
                    break
                except Exception as e:
                    print(e)
                    attempt += 1
                    if attempt < max_attempts:
                        print(f"An error occurred. Retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        error_message_html = """
                            <div style='display: inline-block; border:2px solid red; padding: 4px; border-radius: 5px; margin-bottom: 20px; color: red;'>
                                <strong>网络错误:</strong> 请重试。
                            </div>
                            """
                        full_response = error_message_html
                        waiting_message.empty()
                        message_placeholder.markdown(full_response, unsafe_allow_html=True)

#------------------------------------------------------------------------------------------------------------------------------#


            


            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

else:
    st.sidebar.info(st.session_state.thread_id)

    if user_input:= st.chat_input(""):
        with st.chat_message("user"):
            st.markdown(user_input)
        

    
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.info(
                "此聊天机器人的对话上限已达到。请从侧边栏复制thread_ID。将线thread_ID粘贴到下面的文本框中。"
            )
    st.chat_input(disabled=True)
