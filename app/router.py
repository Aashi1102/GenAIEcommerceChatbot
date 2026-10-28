from semantic_router import Route, IndexedRouter
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

faq = Route(
    name = "faq",
    utterances = [
        "What is your return policy of the product?",
        "Do i get discount with the HDF credit card?",
        "How can I track my order?,"
        "What payments methods are accepted?",
        "How long does it take to process a refund?",
    ]
)


sql = Route(
    name = "sql",
    utterances = [
        "I want to buy nike shoes that have 50percent discount",
        "I want to buy a red dress that is under $100",
        "I want to buy a black leather jacket that is on sale",
        "I want to buy a pair of running shoes that are on clearance",
        "Are there any deals on laptops that are under $500?",
    ]
)

router = IndexedRouter(
    encoder=encoder,
    routes=[faq, sql]
)


if __name__ == "__main__":
        result = router("How can I track my order?")
        print(result.name if result else "No matching route")
