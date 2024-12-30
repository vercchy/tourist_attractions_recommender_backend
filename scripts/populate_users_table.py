from app.service.authentication.register_service import RegisterService
from app.schemas.authentication_schemas import RegisterRequest
from app.models.city import City
import random

category_descriptions = {
    1: [
        "I'm really fascinated by both ancient and modern architecture. I love exploring historical buildings, such as castles and old churches, but also enjoy visiting cutting-edge skyscrapers, urban designs, and futuristic buildings. I'd love to see the contrast between traditional and contemporary styles in different cities.",
        "I love visiting cities where I can see a mix of historical and architectural landmarks. For example, I want to explore the ancient ruins of Rome, visit architectural wonders like the Colosseum and the Pantheon, and also visit modern architectural masterpieces in the same city, like the MAXXI Museum. I'm interested in how these sites coexist and tell the story of a place’s history and development.",
        "I’m fascinated by architecture, art, and science. I want to visit cities that offer a mix of historical buildings and modern art museums. For example, I’d love to visit the Guggenheim Museum in New York and then explore the architectural wonders of the city, followed by a trip to a science center to see interactive exhibits on physics and architecture."
    ],
    2: [
        "I’m passionate about visiting museums, especially art galleries and history museums. I want to see fine art, sculptures, and exhibitions on ancient civilizations. I’m also interested in museums that showcase local culture, photography, and contemporary art scenes.",
        "I enjoy visiting art museums, but I’m also passionate about science. I want to see exhibitions that combine both, like a science museum with an art gallery section. I'm especially interested in museums that explore the intersection of art and technology, such as digital art exhibitions, science fiction artwork, and historical science exhibits.",
        "I’m fascinated by architecture, art, and science. I want to visit cities that offer a mix of historical buildings and modern art museums. For example, I’d love to visit the Guggenheim Museum in New York and then explore the architectural wonders of the city, followed by a trip to a science center to see interactive exhibits on physics and architecture."
    ],
    3: [
        "I want to explore ancient historical sites, including ruins, palaces, and UNESCO World Heritage Sites. Visiting places like Roman forums, medieval castles, and ancient temples really excites me. I’m particularly interested in learning about the history behind these monuments and how they’ve survived through the ages.",
        "I want to visit cities with a rich cultural history where I can enjoy a live performance in an iconic, historical venue. For instance, I'd love to see Shakespeare plays performed in the Globe Theatre in London, or watch a classical concert in Vienna's historical concert halls, where the history of both the performance and the venue come together.",
        "I’m interested in visiting religious and historical sites, and I also want to experience the local culture. I’d love to visit places like Cairo, where I can explore the Pyramids and historical sites, then visit local markets like the Khan El Khalili Bazaar to experience traditional Egyptian crafts, food, and culture."
    ],
    4: [
        "I have a deep interest in visiting sacred religious sites, such as ancient temples, mosques, and cathedrals. I’m also interested in learning about spiritual practices, so I’d love to visit Buddhist monasteries, Hindu temples, and sacred pilgrimage routes like the Camino de Santiago.",
        "I’m interested in visiting spiritual sites with historical significance, like the temples of Angkor Wat in Cambodia or the churches of Jerusalem. I want to learn about the historical and cultural contexts of these religious monuments while also experiencing their spiritual atmosphere.",
        "I’m interested in visiting religious and historical sites, and I also want to experience the local culture. I’d love to visit places like Cairo, where I can explore the Pyramids and historical sites, then visit local markets like the Khan El Khalili Bazaar to experience traditional Egyptian crafts, food, and culture"
    ],
    5: [
        "I’m a nature lover and enjoy spending time in tranquil parks and botanical gardens. Whether it’s walking through a meticulously maintained garden, admiring rare flowers, or exploring large, wild national parks, I’m always looking for places to connect with nature and enjoy a peaceful environment.",
        "I’m looking for places where I can experience both beautiful beaches and lush gardens. For example, I want to visit tropical islands with stunning coastlines and also explore the nearby botanical gardens, where I can enjoy the peacefulness of nature and then unwind by the beach.",
        "I enjoy visiting places where I can walk through beautiful parks and gardens, but I also love art galleries and museums. I’d like to visit cities like Paris, where I can explore the gardens of the Palace of Versailles and then enjoy exhibitions at the Louvre, all while experiencing the artistic and natural beauty",
        "I’m looking for a vacation where I can experience the best of nature: hiking in the mountains, relaxing on beautiful beaches, and strolling through lush parks and gardens. Places like Hawaii or Costa Rica offer a mix of all three—mountains, beaches, and vibrant gardens."
    ],
    6: [
        "I love outdoor adventures, and hiking in the mountains is one of my favorite activities. I want to discover scenic mountain trails, especially those that lead to panoramic views, waterfalls, or high-altitude lakes. I’d also love to try more challenging hikes and experience different mountain ranges around the world.",
        "I’m passionate about hiking in the mountains and want to visit scenic spots where the trails lead to incredible views. I’d love to hike through the Swiss Alps, where I can experience both the beauty of the mountains and the picturesque alpine meadows, with plenty of scenic overlooks along the way.",
        "I’d love to visit a destination where I can explore both beautiful beaches and rugged mountain trails. I’m interested in places like the Pacific coast of the U.S., where I can hike the cliffs of Big Sur and then relax on the beaches after a day of hiking, all in one trip.",
        "I’m an outdoor enthusiast and want to go on mountain hikes that lead to stunning scenic spots. Whether it's hiking through the Canadian Rockies or exploring the Andes, I want to be able to take in breathtaking views, such as mountain vistas, waterfalls, and dramatic landscapes.",
        "I’m looking for a vacation where I can experience the best of nature: hiking in the mountains, relaxing on beautiful beaches, and strolling through lush parks and gardens. Places like Hawaii or Costa Rica offer a mix of all three—mountains, beaches, and vibrant gardens.",
    ],
    7: [
        "I’m looking for pristine beaches where I can relax, swim, and enjoy the sun. I love visiting coastlines that have clear waters, sandy shores, and opportunities for water sports like snorkeling, kayaking, and surfing. I'm especially drawn to islands and tropical beach destinations",
        "I’m looking for places where I can experience both beautiful beaches and lush gardens. For example, I want to visit tropical islands with stunning coastlines and also explore the nearby botanical gardens, where I can enjoy the peacefulness of nature and then unwind by the beach.",
        "I’d love to visit a destination where I can explore both beautiful beaches and rugged mountain trails. I’m interested in places like the Pacific coast of the U.S., where I can hike the cliffs of Big Sur and then relax on the beaches after a day of hiking, all in one trip.",
        "I’m looking for a vacation where I can experience the best of nature: hiking in the mountains, relaxing on beautiful beaches, and strolling through lush parks and gardens. Places like Hawaii or Costa Rica offer a mix of all three—mountains, beaches, and vibrant gardens."
    ],
    8: [
        "I enjoy attending live performances like theater shows, operas, and ballet. I want to watch famous plays, musicals, and performances in iconic venues such as the Globe Theatre in London or the Sydney Opera House. I’m also interested in local performances that showcase the cultural heritage of a region.",
        "I want to visit cities with a rich cultural history where I can enjoy a live performance in an iconic, historical venue. For instance, I'd love to see Shakespeare plays performed in the Globe Theatre in London, or watch a classical concert in Vienna's historical concert halls, where the history of both the performance and the venue come together.",
        "I’m interested in the intersection of performance arts and science. I’d love to see performances that use technology or science as part of the show, such as interactive theater with projections or performances that use robotics and augmented reality. I’m also interested in visiting science museums that explore art through technological lenses.",
    ],
    9: [
        "I love the thrill of amusement parks and theme parks, especially those with roller coasters and unique rides. Whether it's exploring Disney parks or local funfairs, I’m excited to experience new attractions, meet characters, and try out the latest thrilling rides in various parks around the world.",
        "I want to take my kids to a place where they can enjoy fun rides, games, and entertainment. I’m looking for a destination that has both amusement parks and family-friendly attractions, like theme parks with age-appropriate rides and museums or interactive exhibits for the younger ones.",
        "I want to visit places with stunning natural landscapes and exciting amusement parks. I’m interested in places like Disneyland in California, where I can experience the magic of the park and then take a break to explore nearby natural scenic spots, like the beaches or national parks"
    ],
    10: [
        "I’m always on the lookout for breathtaking scenic spots, like hidden viewpoints, cliffside overlooks, and panoramic vistas. Whether it’s a viewpoint on a mountain hike, a scenic drive through a national park, or a beach with stunning sunset views, I want to capture beautiful landscapes.",
        "I’m passionate about hiking in the mountains and want to visit scenic spots where the trails lead to incredible views. I’d love to hike through the Swiss Alps, where I can experience both the beauty of the mountains and the picturesque alpine meadows, with plenty of scenic overlooks along the way",
        "I want to visit places with stunning natural landscapes and exciting amusement parks. I’m interested in places like Disneyland in California, where I can experience the magic of the park and then take a break to explore nearby natural scenic spots, like the beaches or national parks."
    ],
    11: [
        "I’m fascinated by science, technology, and space exploration, so I love visiting science centers and museums that have interactive exhibits. I want to learn about space at planetariums, explore natural history museums, and engage with hands-on exhibits that teach about physics, biology, and environmental sustainability.",
        "I enjoy visiting art museums, but I’m also passionate about science. I want to see exhibitions that combine both, like a science museum with an art gallery section. I'm especially interested in museums that explore the intersection of art and technology, such as digital art exhibitions, science fiction artwork, and historical science exhibits.",
        "I’m interested in the intersection of performance arts and science. I’d love to see performances that use technology or science as part of the show, such as interactive theater with projections or performances that use robotics and augmented reality. I’m also interested in visiting science museums that explore art through technological lenses",
        "I’m fascinated by architecture, art, and science. I want to visit cities that offer a mix of historical buildings and modern art museums. For example, I’d love to visit the Guggenheim Museum in New York and then explore the architectural wonders of the city, followed by a trip to a science center to see interactive exhibits on physics and architecture."
    ],
    12: [
        "I’m traveling with my family and looking for attractions that offer something for everyone. From interactive museums and amusement parks to zoos, aquariums, and kid-friendly science centers, I want to make sure we visit places that will keep the kids entertained and offer fun for all ages",
        "I want to take my kids to a place where they can enjoy fun rides, games, and entertainment. I’m looking for a destination that has both amusement parks and family-friendly attractions, like theme parks with age-appropriate rides and museums or interactive exhibits for the younger ones",
        "I want to visit places with stunning natural landscapes and exciting amusement parks. I’m interested in places like Disneyland in California, where I can experience the magic of the park and then take a break to explore nearby natural scenic spots, like the beaches or national parks"
    ],
    13: [
        "I’m interested in exploring local markets where I can find fresh produce, traditional food, handmade crafts, and unique souvenirs. I love the hustle and bustle of local market stalls and enjoy trying street food or buying authentic items that reflect the culture of the place I’m visiting.",
        "I’m interested in visiting religious and historical sites, and I also want to experience the local culture. I’d love to visit places like Cairo, where I can explore the Pyramids and historical sites, then visit local markets like the Khan El Khalili Bazaar to experience traditional Egyptian crafts, food, and culture.",
    ]
}

def create_random_users(glove_model, db, num_users=500):
    register_service = RegisterService(db, glove_model)

    for i in range(num_users):
        country_id = random.randint(1, 198)
        cities = db.query(City).filter(City.country_id == country_id).all()
        if cities:
            city_id = random.choice(cities).id
        num_categories = random.randint(1, 3)
        selected_categories = random.sample(range(1, 14), num_categories)
        single_category = random.choice(selected_categories)
        description_of_interests = random.choice(category_descriptions[single_category])
        register_request = RegisterRequest(
            first_name=f"User{i}",
            last_name=f"LastName{i}",
            date_of_birth="1991-01-01",
            email=f"user{i}@gmail.com",
            password="password123",
            country_id=country_id,
            city_id=city_id,
            interests=description_of_interests,
            preferences=selected_categories
        )

        register_service.register(register_request)

