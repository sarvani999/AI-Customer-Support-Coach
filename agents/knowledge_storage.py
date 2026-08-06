import json
import os
import re
import uuid

from datetime import datetime


class KnowledgeStorage:
    """
    Stores uploaded knowledge documents
    and performs simple keyword-based retrieval.
    """

    def __init__(self):

        backend_folder = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.storage_folder = os.path.join(
            backend_folder,
            "knowledge_data"
        )

        self.upload_folder = os.path.join(
            self.storage_folder,
            "uploads"
        )

        self.database_file = os.path.join(
            self.storage_folder,
            "knowledge_base.json"
        )

        os.makedirs(
            self.storage_folder,
            exist_ok=True
        )

        os.makedirs(
            self.upload_folder,
            exist_ok=True
        )

        self._ensure_database()


    def _ensure_database(self):
        """
        Creates the JSON database file
        when it does not exist.
        """

        if os.path.exists(
            self.database_file
        ):
            return

        initial_data = {
            "documents": [],
            "chunks": []
        }

        self._save_database(
            initial_data
        )


    def _load_database(self):
        """
        Loads the current knowledge database.
        """

        try:

            with open(
                self.database_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            data = {
                "documents": [],
                "chunks": []
            }

        if not isinstance(
            data,
            dict
        ):

            data = {
                "documents": [],
                "chunks": []
            }

        data.setdefault(
            "documents",
            []
        )

        data.setdefault(
            "chunks",
            []
        )

        return data


    def _save_database(
        self,
        data
    ):
        """
        Saves knowledge data to JSON.
        """

        with open(
            self.database_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )


    def _normalize_text(
        self,
        value
    ):
        """
        Normalizes text for searching.
        """

        text = str(
            value or ""
        ).strip().lower()

        text = re.sub(
            r"[^a-z0-9\u0C00-\u0C7F\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    def _safe_filename(
        self,
        filename
    ):
        """
        Removes unsafe characters
        from uploaded filenames.
        """

        filename = os.path.basename(
            str(
                filename or "document"
            )
        )

        filename = re.sub(
            r"[^a-zA-Z0-9._-]",
            "_",
            filename
        )

        return filename

    def _extract_text_from_txt(
        self,
        file_path
    ):
        """
        Extracts text from TXT files.
        """

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            return file.read()


    def _extract_text_from_pdf(
        self,
        file_path
    ):
        """
        Extracts text from PDF files
        using PyMuPDF.
        """

        try:
            import fitz

        except ImportError as error:

            raise ImportError(
                "PyMuPDF is not installed. "
                "Run: pip install pymupdf"
            ) from error

        document = fitz.open(
            file_path
        )

        pages = []

        try:

            for page_number in range(
                len(document)
            ):

                page = document.load_page(
                    page_number
                )

                page_text = page.get_text(
                    "text"
                )

                pages.append({
                    "page_number":
                        page_number + 1,
                    "text":
                        page_text
                })

        finally:

            document.close()

        return pages


    def _extract_text_from_docx(
        self,
        file_path
    ):
        """
        Extracts text from DOCX files.
        """

        try:
            from docx import Document

        except ImportError as error:

            raise ImportError(
                "python-docx is not installed. "
                "Run: pip install python-docx"
            ) from error

        document = Document(
            file_path
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            text = str(
                paragraph.text or ""
            ).strip()

            if text:

                paragraphs.append(
                    text
                )

        return "\n".join(
            paragraphs
        )


    def _extract_document_text(
        self,
        file_path
    ):
        """
        Extracts text based on file type.

        Returns:
        {
            "full_text": "...",
            "pages": [...]
        }
        """

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".pdf":

            pages = self._extract_text_from_pdf(
                file_path
            )

            full_text = "\n\n".join(
                [
                    page.get(
                        "text",
                        ""
                    )
                    for page in pages
                ]
            )

            return {
                "full_text":
                    full_text,
                "pages":
                    pages
            }

        if extension == ".txt":

            full_text = self._extract_text_from_txt(
                file_path
            )

            return {
                "full_text":
                    full_text,
                "pages": [
                    {
                        "page_number": 1,
                        "text": full_text
                    }
                ]
            }

        if extension == ".docx":

            full_text = self._extract_text_from_docx(
                file_path
            )

            return {
                "full_text":
                    full_text,
                "pages": [
                    {
                        "page_number": 1,
                        "text": full_text
                    }
                ]
            }

        raise ValueError(
            "Unsupported file type. "
            "Only PDF, DOCX, and TXT files are allowed."
        )


    def _clean_extracted_text(
        self,
        text
    ):
        """
        Cleans extracted document text.
        """

        clean_text = str(
            text or ""
        )

        clean_text = clean_text.replace(
            "\x00",
            " "
        )

        clean_text = re.sub(
            r"[ \t]+",
            " ",
            clean_text
        )

        clean_text = re.sub(
            r"\n{3,}",
            "\n\n",
            clean_text
        )

        return clean_text.strip()


    def _chunk_text(
        self,
        text,
        chunk_size=900,
        overlap=150
    ):
        """
        Splits document text into overlapping chunks.
        """

        clean_text = self._clean_extracted_text(
            text
        )

        if not clean_text:

            return []

        if chunk_size <= 0:

            raise ValueError(
                "Chunk size must be greater than zero."
            )

        if overlap < 0:

            overlap = 0

        if overlap >= chunk_size:

            overlap = chunk_size // 4

        chunks = []

        start = 0

        text_length = len(
            clean_text
        )

        while start < text_length:

            end = min(
                start + chunk_size,
                text_length
            )

            chunk = clean_text[
                start:end
            ]

            if end < text_length:

                last_period = max(
                    chunk.rfind(". "),
                    chunk.rfind("? "),
                    chunk.rfind("! "),
                    chunk.rfind("\n")
                )

                if last_period > (
                    chunk_size // 2
                ):

                    end = start + last_period + 1

                    chunk = clean_text[
                        start:end
                    ]

            chunk = chunk.strip()

            if chunk:

                chunks.append(
                    chunk
                )

            if end >= text_length:

                break

            next_start = end - overlap

            if next_start <= start:

                next_start = end

            start = next_start

        return chunks


    def _find_page_number(
        self,
        chunk_text,
        pages
    ):
        """
        Tries to identify the page number
        where a chunk belongs.
        """

        normalized_chunk = (
            self._normalize_text(
                chunk_text
            )
        )

        if not normalized_chunk:

            return None

        chunk_words = normalized_chunk.split()

        sample = " ".join(
            chunk_words[:12]
        )

        if not sample:

            return None

        for page in pages:

            page_text = self._normalize_text(
                page.get(
                    "text",
                    ""
                )
            )

            if sample in page_text:

                return page.get(
                    "page_number"
                )

        return None

    def add_document(
        self,
        file_storage,
        product,
        scenario,
        title=None
    ):
        """
        Saves an uploaded file, extracts its text,
        creates chunks, and stores document metadata.
        """

        if file_storage is None:

            raise ValueError(
                "Knowledge file is required."
            )

        original_filename = str(
            file_storage.filename or ""
        ).strip()

        if not original_filename:

            raise ValueError(
                "Uploaded file name is missing."
            )

        safe_filename = self._safe_filename(
            original_filename
        )

        extension = os.path.splitext(
            safe_filename
        )[1].lower()

        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        if extension not in allowed_extensions:

            raise ValueError(
                "Unsupported file type. "
                "Only PDF, DOCX, and TXT files are allowed."
            )

        product_name = str(
            product or "General"
        ).strip()

        scenario_name = str(
            scenario or "General Support"
        ).strip()

        document_title = str(
            title or ""
        ).strip()

        if not document_title:

            document_title = os.path.splitext(
                original_filename
            )[0]

        document_id = str(
            uuid.uuid4()
        )

        unique_filename = (
            f"{document_id}_"
            f"{safe_filename}"
        )

        saved_file_path = os.path.join(
            self.upload_folder,
            unique_filename
        )

        file_storage.save(
            saved_file_path
        )

        try:

            extracted_data = (
                self._extract_document_text(
                    saved_file_path
                )
            )

            full_text = (
                self._clean_extracted_text(
                    extracted_data.get(
                        "full_text",
                        ""
                    )
                )
            )

            pages = extracted_data.get(
                "pages",
                []
            )

            if not full_text:

                raise ValueError(
                    "No readable text was found "
                    "inside the uploaded document."
                )

            text_chunks = self._chunk_text(
                full_text
            )

            if not text_chunks:

                raise ValueError(
                    "No knowledge chunks could be "
                    "created from the uploaded document."
                )

            database = self._load_database()

            uploaded_at = (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            )

            document_record = {
                "document_id":
                    document_id,
                "title":
                    document_title,
                "file_name":
                    original_filename,
                "stored_file_name":
                    unique_filename,
                "product":
                    product_name,
                "scenario":
                    scenario_name,
                "file_type":
                    extension.replace(
                        ".",
                        ""
                    ).upper(),
                "file_path":
                    saved_file_path,
                "characters_extracted":
                    len(full_text),
                "pages_processed":
                    len(pages),
                "chunks_created":
                    len(text_chunks),
                "status":
                    "Ready",
                "uploaded_at":
                    uploaded_at
            }

            chunk_records = []

            for index, chunk_text in enumerate(
                text_chunks,
                start=1
            ):

                chunk_id = str(
                    uuid.uuid4()
                )

                page_number = (
                    self._find_page_number(
                        chunk_text,
                        pages
                    )
                )

                chunk_record = {
                    "chunk_id":
                        chunk_id,
                    "document_id":
                        document_id,
                    "chunk_number":
                        index,
                    "title":
                        document_title,
                    "file_name":
                        original_filename,
                    "product":
                        product_name,
                    "scenario":
                        scenario_name,
                    "page_number":
                        page_number,
                    "content":
                        chunk_text,
                    "normalized_content":
                        self._normalize_text(
                            chunk_text
                        ),
                    "uploaded_at":
                        uploaded_at
                }

                chunk_records.append(
                    chunk_record
                )

            database[
                "documents"
            ].append(
                document_record
            )

            database[
                "chunks"
            ].extend(
                chunk_records
            )

            self._save_database(
                database
            )

            return {
                "status":
                    "success",
                "message":
                    "Knowledge document uploaded successfully.",
                "document":
                    document_record,
                "chunks":
                    chunk_records
            }

        except Exception:

            if os.path.exists(
                saved_file_path
            ):

                os.remove(
                    saved_file_path
                )

            raise


    def list_documents(
        self
    ):
        """
        Returns all uploaded knowledge documents,
        newest first.
        """

        database = self._load_database()

        documents = database.get(
            "documents",
            []
        )

        documents = sorted(
            documents,
            key=lambda item: item.get(
                "uploaded_at",
                ""
            ),
            reverse=True
        )

        return documents


    def get_document(
        self,
        document_id
    ):
        """
        Returns one uploaded document
        using its document ID.
        """

        database = self._load_database()

        for document in database.get(
            "documents",
            []
        ):

            if (
                document.get(
                    "document_id"
                )
                ==
                document_id
            ):

                return document

        return None


    def get_document_chunks(
        self,
        document_id
    ):
        """
        Returns all chunks belonging
        to one uploaded document.
        """

        database = self._load_database()

        chunks = [
            chunk
            for chunk in database.get(
                "chunks",
                []
            )
            if chunk.get(
                "document_id"
            )
            ==
            document_id
        ]

        return sorted(
            chunks,
            key=lambda item: item.get(
                "chunk_number",
                0
            )
        )
    def search(
        self,
        query,
        product=None,
        scenario=None,
        top_k=3
    ):
        """
        Searches uploaded knowledge using
        simple keyword scoring.
        """

        query = self._normalize_text(
            query
        )

        if not query:

            return []

        database = self._load_database()

        chunks = database.get(
            "chunks",
            []
        )

        query_words = set(
            query.split()
        )

        results = []

        for chunk in chunks:

            score = 0

            chunk_text = chunk.get(
                "normalized_content",
                ""
            )

            chunk_words = set(
                chunk_text.split()
            )

            common_words = (
                query_words &
                chunk_words
            )

            score += (
                len(common_words) * 5
            )

            if product:

                if (
                    self._normalize_text(
                        chunk.get(
                            "product",
                            ""
                        )
                    )
                    ==
                    self._normalize_text(
                        product
                    )
                ):

                    score += 20

            if scenario:

                if (
                    self._normalize_text(
                        chunk.get(
                            "scenario",
                            ""
                        )
                    )
                    ==
                    self._normalize_text(
                        scenario
                    )
                ):

                    score += 30

            if score <= 0:

                continue

            result = dict(
                chunk
            )

            result[
                "confidence"
            ] = min(
                100,
                score
            )

            results.append(
                result
            )

        results.sort(
            key=lambda item: item.get(
                "confidence",
                0
            ),
            reverse=True
        )

        return results[
            :top_k
        ]


    def delete_document(
        self,
        document_id
    ):
        """
        Deletes one uploaded document
        and all its chunks.
        """

        database = self._load_database()

        documents = database.get(
            "documents",
            []
        )

        document = None

        remaining_documents = []

        for item in documents:

            if (
                item.get(
                    "document_id"
                )
                ==
                document_id
            ):

                document = item

            else:

                remaining_documents.append(
                    item
                )

        if document is None:

            return False

        file_path = document.get(
            "file_path"
        )

        if (
            file_path and
            os.path.exists(
                file_path
            )
        ):

            try:

                os.remove(
                    file_path
                )

            except Exception:

                pass

        remaining_chunks = [

            chunk

            for chunk in database.get(
                "chunks",
                []
            )

            if (
                chunk.get(
                    "document_id"
                )
                !=
                document_id
            )

        ]

        database[
            "documents"
        ] = remaining_documents

        database[
            "chunks"
        ] = remaining_chunks

        self._save_database(
            database
        )

        return True


    def get_statistics(
        self
    ):
        """
        Returns overall knowledge-base statistics.
        """

        database = self._load_database()

        documents = database.get(
            "documents",
            []
        )

        chunks = database.get(
            "chunks",
            []
        )

        return {

            "documents":
                len(
                    documents
                ),

            "chunks":
                len(
                    chunks
                ),

            "products":
                len(
                    set(
                        doc.get(
                            "product",
                            ""
                        )
                        for doc
                        in documents
                    )
                ),

            "scenarios":
                len(
                    set(
                        doc.get(
                            "scenario",
                            ""
                        )
                        for doc
                        in documents
                    )
                )

        }


knowledge_storage = (
    KnowledgeStorage()
)