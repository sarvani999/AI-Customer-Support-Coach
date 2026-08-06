from flask import (
    jsonify,
    render_template,
    request
)

from agents.knowledge_storage import (
    knowledge_storage
)


def register_knowledge_routes(
    app
):
    """
    Registers all Knowledge Base
    page and API routes.
    """

    @app.route(
        "/knowledge-base",
        methods=["GET"]
    )
    def knowledge_base_page():
        """
        Opens the Knowledge Base page.
        """

        return render_template(
            "knowledge_base.html"
        )


    @app.route(
        "/upload-knowledge",
        methods=["POST"]
    )
    def upload_knowledge():
        """
        Uploads a PDF, DOCX, or TXT file,
        extracts its text, creates chunks,
        and stores it in the Knowledge Base.
        """

        try:

            uploaded_file = request.files.get(
                "file"
            )

            product = str(
                request.form.get(
                    "product",
                    "General"
                )
            ).strip()

            scenario = str(
                request.form.get(
                    "scenario",
                    "General Support"
                )
            ).strip()

            title = str(
                request.form.get(
                    "title",
                    ""
                )
            ).strip()

            if uploaded_file is None:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Please select a knowledge file."
                }), 400

            if not uploaded_file.filename:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Uploaded file name is missing."
                }), 400

            if not product:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Product is required."
                }), 400

            if not scenario:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Scenario is required."
                }), 400

            result = (
                knowledge_storage.add_document(
                    file_storage=
                        uploaded_file,
                    product=
                        product,
                    scenario=
                        scenario,
                    title=
                        title or None
                )
            )

            document = result.get(
                "document",
                {}
            )

            return jsonify({
                "status":
                    "success",
                "message":
                    result.get(
                        "message",
                        "Knowledge document uploaded successfully."
                    ),
                "document":
                    document,
                "processing_result": {
                    "file_name":
                        document.get(
                            "file_name",
                            ""
                        ),
                    "product":
                        document.get(
                            "product",
                            product
                        ),
                    "scenario":
                        document.get(
                            "scenario",
                            scenario
                        ),
                    "file_type":
                        document.get(
                            "file_type",
                            ""
                        ),
                    "pages_processed":
                        document.get(
                            "pages_processed",
                            0
                        ),
                    "chunks_created":
                        document.get(
                            "chunks_created",
                            0
                        ),
                    "characters_extracted":
                        document.get(
                            "characters_extracted",
                            0
                        ),
                    "status":
                        document.get(
                            "status",
                            "Ready"
                        )
                }
            }), 201

        except (
            ValueError,
            ImportError
        ) as error:

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 400

        except Exception as error:

            print(
                "UPLOAD KNOWLEDGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    @app.route(
        "/knowledge-documents",
        methods=["GET"]
    )
    def knowledge_documents():
        """
        Returns all uploaded
        Knowledge Base documents.
        """

        try:

            documents = (
                knowledge_storage
                .list_documents()
            )

            statistics = (
                knowledge_storage
                .get_statistics()
            )

            return jsonify({
                "status":
                    "success",
                "documents":
                    documents,
                "statistics":
                    statistics
            }), 200

        except Exception as error:

            print(
                "LIST KNOWLEDGE DOCUMENTS ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    @app.route(
        "/knowledge-document/<document_id>",
        methods=["GET"]
    )
    def knowledge_document(
        document_id
    ):
        """
        Returns one document
        and all its text chunks.
        """

        try:

            document = (
                knowledge_storage
                .get_document(
                    document_id
                )
            )

            if document is None:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Knowledge document was not found."
                }), 404

            chunks = (
                knowledge_storage
                .get_document_chunks(
                    document_id
                )
            )

            return jsonify({
                "status":
                    "success",
                "document":
                    document,
                "chunks":
                    chunks
            }), 200

        except Exception as error:

            print(
                "GET KNOWLEDGE DOCUMENT ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    @app.route(
        "/search-knowledge",
        methods=["POST"]
    )
    def search_knowledge():
        """
        Searches uploaded Knowledge Base
        chunks using a user question.
        """

        try:

            data = request.get_json(
                silent=True
            ) or {}

            query = str(
                data.get(
                    "query",
                    data.get(
                        "question",
                        ""
                    )
                )
            ).strip()

            product = str(
                data.get(
                    "product",
                    ""
                )
            ).strip()

            scenario = str(
                data.get(
                    "scenario",
                    ""
                )
            ).strip()

            top_k = data.get(
                "top_k",
                3
            )

            try:

                top_k = int(
                    top_k
                )

            except (
                TypeError,
                ValueError
            ):

                top_k = 3

            top_k = max(
                1,
                min(
                    10,
                    top_k
                )
            )

            if not query:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Please enter a search question."
                }), 400

            results = (
                knowledge_storage.search(
                    query=
                        query,
                    product=
                        product or None,
                    scenario=
                        scenario or None,
                    top_k=
                        top_k
                )
            )

            if not results:

                return jsonify({
                    "status":
                        "success",
                    "message":
                        "No matching uploaded knowledge was found.",
                    "results":
                        [],
                    "best_match":
                        None
                }), 200

            best_match = results[0]

            return jsonify({
                "status":
                    "success",
                "message":
                    "Relevant knowledge was found.",
                "best_match": {
                    "title":
                        best_match.get(
                            "title",
                            "Uploaded Knowledge"
                        ),
                    "content":
                        best_match.get(
                            "content",
                            ""
                        ),
                    "source":
                        best_match.get(
                            "file_name",
                            "Uploaded document"
                        ),
                    "product":
                        best_match.get(
                            "product",
                            ""
                        ),
                    "scenario":
                        best_match.get(
                            "scenario",
                            ""
                        ),
                    "page_number":
                        best_match.get(
                            "page_number"
                        ),
                    "confidence":
                        best_match.get(
                            "confidence",
                            0
                        )
                },
                "results":
                    results
            }), 200

        except Exception as error:

            print(
                "SEARCH KNOWLEDGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    @app.route(
        "/delete-knowledge/<document_id>",
        methods=["DELETE"]
    )
    def delete_knowledge(
        document_id
    ):
        """
        Deletes one Knowledge Base document
        and all its stored chunks.
        """

        try:

            deleted = (
                knowledge_storage
                .delete_document(
                    document_id
                )
            )

            if not deleted:

                return jsonify({
                    "status":
                        "error",
                    "message":
                        "Knowledge document was not found."
                }), 404

            return jsonify({
                "status":
                    "success",
                "message":
                    "Knowledge document deleted successfully."
            }), 200

        except Exception as error:

            print(
                "DELETE KNOWLEDGE ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500


    @app.route(
        "/knowledge-statistics",
        methods=["GET"]
    )
    def knowledge_statistics():
        """
        Returns Knowledge Base statistics.
        """

        try:

            statistics = (
                knowledge_storage
                .get_statistics()
            )

            return jsonify({
                "status":
                    "success",
                "statistics":
                    statistics
            }), 200

        except Exception as error:

            print(
                "KNOWLEDGE STATISTICS ERROR =",
                error
            )

            return jsonify({
                "status":
                    "error",
                "message":
                    str(error)
            }), 500